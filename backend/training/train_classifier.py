import argparse
import time
from pathlib import Path
import cv2
import numpy as np
import torch
from tqdm import tqdm
from matplotlib.figure import Figure
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision.transforms import v2
from core.constants.paths import PROJECT_ROOT
from core.constants.waste import WASTE_CATEGORY_LABELS
from modules.classification.services.image_preprocessor.service import ImagePreprocessor
from modules.classification.services.waste_classifier.utils import (
    MODEL_NAME,
    build_waste_classifier_model,
    get_normalization,
    preprocess_crops,
)
from training.common import (
    MANIFEST_CSV,
    classifier_weights_path,
    log_experiment,
    manifest_clahe_baked,
    read_manifest,
    report_dir,
    seed_everything,
    write_csv_report,
    write_json_report,
)

HISTORY_COLUMNS = [
    "phase",
    "epoch",
    "learning_rate",
    "train_loss",
    "train_accuracy",
    "val_loss",
    "val_accuracy",
    "seconds",
]


class WasteImageDataset(Dataset):
    def __init__(
        self,
        rows: list[dict],
        image_size: int,
        mean: tuple[float, ...],
        std: tuple[float, ...],
        augment: bool,
        clahe: bool = True,
    ) -> None:
        self._rows = rows
        self._image_size = image_size
        self._mean = mean
        self._std = std
        self._augment = augment
        self._clahe = clahe
        self._preprocessor: ImagePreprocessor | None = None
        self._augmentation = v2.Compose(
            [
                v2.RandomResizedCrop(
                    (image_size, image_size), scale=(0.6, 1.0), antialias=True
                ),
                v2.RandomHorizontalFlip(),
                v2.RandomRotation(15),
                v2.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.02),
                v2.ToDtype(torch.float32, scale=True),
                v2.Normalize(mean=list(mean), std=list(std)),
            ]
        )

    def __len__(self) -> int:
        return len(self._rows)

    def __getstate__(self):
        state = self.__dict__.copy()
        state["_preprocessor"] = None
        return state

    def __getitem__(self, index: int) -> tuple[torch.Tensor, int]:
        if self._clahe and self._preprocessor is None:
            self._preprocessor = ImagePreprocessor()

        row = self._rows[index]
        bgr = cv2.imdecode(
            np.fromfile(PROJECT_ROOT / row["path"], dtype=np.uint8), cv2.IMREAD_COLOR
        )
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        if self._clahe:
            rgb = self._preprocessor.process(rgb)
        label = WASTE_CATEGORY_LABELS.index(row["kelas"])

        if self._augment:
            tensor = torch.from_numpy(rgb.transpose(2, 0, 1).copy())
            return self._augmentation(tensor), label

        return preprocess_crops([rgb], self._image_size, self._mean, self._std)[0], label


def main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tuning MobileNetV4-Conv-S 4 kelas")
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--batch", type=int, default=64)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--freeze-epochs", type=int, default=5)
    parser.add_argument("--finetune-epochs", type=int, default=25)
    parser.add_argument("--head-lr", type=float, default=1e-3)
    parser.add_argument("--finetune-lr", type=float, default=1e-4)
    parser.add_argument("--weight-decay", type=float, default=0.05)
    parser.add_argument(
        "--unfreeze-stages",
        type=int,
        default=2,
        help="Jumlah stage terakhir backbone yang dilatih di fase 2 (-1 = semua).",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--limit", type=int, default=0, help="Untuk uji cepat saja.")
    parser.add_argument(
        "--name",
        default=None,
        help="Kode eksperimen (mis. K1). Bobot ke models/classifier/<kode>/, "
        "laporan ke reports/eksperimen/<kode>/. Kosong = lokasi bawaan.",
    )
    parser.add_argument("--no-clahe", action="store_true", help="Latih tanpa CLAHE.")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=MANIFEST_CSV,
        help="Manifest lain, mis. data/classification_crops/manifest.csv (eksperimen K4).",
    )
    parser.add_argument("--keterangan", default="", help="Catatan singkat eksperimen.")
    options = parser.parse_args()
    clahe = not options.no_clahe
    baked = manifest_clahe_baked(options.manifest)
    if baked and options.no_clahe:
        raise SystemExit("Manifest ini sudah melalui CLAHE; --no-clahe tidak berlaku.")
    weights_path = classifier_weights_path(options.name)

    seed_everything(options.seed)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    model = build_waste_classifier_model(pretrained=True).to(device)
    mean, std = get_normalization(model)

    rows = read_manifest(options.manifest)
    train_rows = [row for row in rows if row["split"] == "train"]
    val_rows = [row for row in rows if row["split"] == "val"]
    if options.limit:
        train_rows, val_rows = train_rows[: options.limit], val_rows[: options.limit]
    print(f"Data latih: {len(train_rows)}, data validasi: {len(val_rows)}, CLAHE: {clahe}")

    loader_args = {
        "batch_size": options.batch,
        "num_workers": options.workers,
        "pin_memory": device.type == "cuda",
        "persistent_workers": options.workers > 0,
    }
    train_loader = DataLoader(
        WasteImageDataset(
            train_rows, options.image_size, mean, std, augment=True, clahe=clahe and not baked
        ),
        shuffle=True,
        drop_last=len(train_rows) > options.batch,
        **loader_args,
    )
    val_loader = DataLoader(
        WasteImageDataset(
            val_rows, options.image_size, mean, std, augment=False, clahe=clahe and not baked
        ),
        shuffle=False,
        **loader_args,
    )

    criterion = nn.CrossEntropyLoss()
    scaler = torch.amp.GradScaler(enabled=device.type == "cuda")

    history: list[dict] = []
    best = {"val_accuracy": -1.0, "epoch": 0, "phase": ""}
    phases = [
        ("freeze", options.freeze_epochs, options.head_lr, 0),
        (
            "finetune",
            options.finetune_epochs,
            options.finetune_lr,
            options.unfreeze_stages,
        ),
    ]
    for phase, epochs, lr, unfreeze_stages in phases:
        if epochs <= 0:
            continue
        frozen = configure_trainable(model, unfreeze_stages)
        optimizer = torch.optim.AdamW(
            [p for p in model.parameters() if p.requires_grad],
            lr=lr,
            weight_decay=options.weight_decay,
        )
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

        for epoch in range(1, epochs + 1):
            started_at = time.perf_counter()
            current_lr = optimizer.param_groups[0]["lr"]
            label = f"{phase} epoch {epoch}/{epochs}"
            train_loss, train_acc = train_one_epoch(
                model, frozen, train_loader, criterion, optimizer, scaler, device,
                desc=f"{label} latih",
            )
            val_loss, val_acc = evaluate(
                model, val_loader, criterion, device, desc=f"{label} validasi"
            )
            scheduler.step()

            row = {
                "phase": phase,
                "epoch": epoch,
                "learning_rate": current_lr,
                "train_loss": round(train_loss, 5),
                "train_accuracy": round(train_acc, 5),
                "val_loss": round(val_loss, 5),
                "val_accuracy": round(val_acc, 5),
                "seconds": round(time.perf_counter() - started_at, 1),
            }
            history.append(row)
            print(row)

            if val_acc > best["val_accuracy"]:
                best = {"val_accuracy": val_acc, "epoch": epoch, "phase": phase}
                save_checkpoint(model, options, mean, std, best, weights_path, clahe)

    history_path = write_csv_report(
        "classifier_training_history.csv", history, HISTORY_COLUMNS, options.name
    )
    plot_history(history, options.name)
    report = write_json_report(
        "classifier_training.json",
        {
            "model": MODEL_NAME,
            "labels": list(WASTE_CATEGORY_LABELS),
            "train_images": len(train_rows),
            "val_images": len(val_rows),
            "clahe": clahe,
            "options": {k: str(v) if isinstance(v, Path) else v for k, v in vars(options).items()},
            "best": best,
            "weights": weights_path.as_posix(),
        },
        options.name,
    )
    log_experiment(
        {
            "kode": options.name or "bawaan",
            "tahap": "B-klasifikasi",
            "langkah": "latih",
            "split": "val",
            "clahe": clahe,
            "keterangan": options.keterangan
            or f"unfreeze={options.unfreeze_stages}, manifest={options.manifest.name}",
            "accuracy": best["val_accuracy"],
            "bobot": weights_path.as_posix(),
            "laporan": report.as_posix(),
        }
    )
    print(f"Bobot terbaik: {weights_path} ({best})")
    print(f"Riwayat: {history_path}")
    print(f"Laporan: {report}")


def configure_trainable(model: nn.Module, unfreeze_stages: int) -> list[nn.Module]:
    stages = list(model.blocks)
    if unfreeze_stages < 0:
        trainable_stages = stages
    else:
        trainable_stages = (
            stages[len(stages) - unfreeze_stages :] if unfreeze_stages else []
        )

    head = [model.conv_head, model.norm_head, model.classifier]
    trainable = [*trainable_stages, *head]
    if unfreeze_stages < 0:
        trainable += [model.conv_stem, model.bn1]

    for parameter in model.parameters():
        parameter.requires_grad = False
    for module in trainable:
        for parameter in module.parameters():
            parameter.requires_grad = True

    trainable_ids = {id(module) for module in trainable}
    frozen = [
        module
        for module in [model.conv_stem, model.bn1, *stages]
        if id(module) not in trainable_ids
    ]
    print(
        "Parameter dilatih: "
        f"{sum(p.numel() for p in model.parameters() if p.requires_grad):,}"
    )
    return frozen


def train_one_epoch(model, frozen, loader, criterion, optimizer, scaler, device, desc="latih"):
    model.train()
    for module in frozen:
        module.eval()

    total_loss, correct, count = 0.0, 0, 0
    progress = tqdm(loader, desc=desc, leave=False, dynamic_ncols=True)
    for images, labels in progress:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)
        optimizer.zero_grad(set_to_none=True)
        with torch.autocast(device_type=device.type, enabled=device.type == "cuda"):
            logits = model(images)
            loss = criterion(logits, labels)
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

        total_loss += loss.item() * labels.size(0)
        correct += (logits.argmax(dim=1) == labels).sum().item()
        count += labels.size(0)
        progress.set_postfix(loss=f"{total_loss / count:.4f}", acc=f"{correct / count:.4f}")
    return total_loss / max(count, 1), correct / max(count, 1)


@torch.inference_mode()
def evaluate(model, loader, criterion, device, desc="validasi"):
    model.eval()
    total_loss, correct, count = 0.0, 0, 0
    for images, labels in tqdm(loader, desc=desc, leave=False, dynamic_ncols=True):
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)
        with torch.autocast(device_type=device.type, enabled=device.type == "cuda"):
            logits = model(images)
            loss = criterion(logits.float(), labels)
        total_loss += loss.item() * labels.size(0)
        correct += (logits.argmax(dim=1) == labels).sum().item()
        count += labels.size(0)
    return total_loss / max(count, 1), correct / max(count, 1)


def save_checkpoint(
    model, options, mean, std, best: dict, weights_path: Path, clahe: bool
) -> None:
    weights_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_name": MODEL_NAME,
            "state_dict": {k: v.detach().cpu() for k, v in model.state_dict().items()},
            "labels": list(WASTE_CATEGORY_LABELS),
            "image_size": options.image_size,
            "mean": list(mean),
            "std": list(std),
            "epoch": best["epoch"],
            "phase": best["phase"],
            "val_accuracy": best["val_accuracy"],
            "clahe": clahe,
        },
        weights_path,
    )


def plot_history(history: list[dict], experiment: str | None = None) -> None:
    if not history:
        return
    steps = range(1, len(history) + 1)
    figure = Figure(figsize=(11, 4))
    loss_axis, acc_axis = figure.subplots(1, 2)
    loss_axis.plot(steps, [h["train_loss"] for h in history], label="latih")
    loss_axis.plot(steps, [h["val_loss"] for h in history], label="validasi")
    loss_axis.set_title("Loss")
    acc_axis.plot(steps, [h["train_accuracy"] for h in history], label="latih")
    acc_axis.plot(steps, [h["val_accuracy"] for h in history], label="validasi")
    acc_axis.set_title("Akurasi")
    for axis in (loss_axis, acc_axis):
        axis.set_xlabel("Epoch (gabungan fase)")
        axis.legend()
        axis.grid(alpha=0.3)
    figure.tight_layout()
    figure.savefig(report_dir(experiment) / "classifier_training_history.png", dpi=150)


if __name__ == "__main__":
    main()
