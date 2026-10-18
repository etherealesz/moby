const JPEG_QUALITY = 0.8;

export class CameraController {
  private stream: MediaStream | null = null;
  private readonly canvas = document.createElement('canvas');

  constructor(private readonly video: HTMLVideoElement) {}

  get deviceId(): string | null {
    return this.stream?.getVideoTracks()[0]?.getSettings().deviceId ?? null;
  }

  get frameSize() {
    return { width: this.video.videoWidth, height: this.video.videoHeight };
  }

  async startStream(deviceId?: string | null) {
    this.stopStream();
    this.stream = await navigator.mediaDevices.getUserMedia({
      audio: false,
      video: deviceId
        ? { deviceId: { exact: deviceId } }
        : { facingMode: { ideal: 'environment' } },
    });
    this.video.srcObject = this.stream;
    await this.video.play();
  }

  stopStream() {
    this.stream?.getTracks().forEach((track) => track.stop());
    this.stream = null;
    this.video.srcObject = null;
  }

  captureFrame(): Promise<Blob> {
    const { width, height } = this.frameSize;
    const context = this.canvas.getContext('2d');
    if (!this.stream || !context || width === 0 || height === 0) {
      return Promise.reject(new Error('Kamera belum siap.'));
    }

    this.canvas.width = width;
    this.canvas.height = height;
    context.drawImage(this.video, 0, 0, width, height);

    return new Promise((resolve, reject) => {
      this.canvas.toBlob(
        (blob) =>
          blob ? resolve(blob) : reject(new Error('Gagal menangkap frame.')),
        'image/jpeg',
        JPEG_QUALITY
      );
    });
  }
}

export function describeCameraError(error: unknown) {
  const name = error instanceof DOMException ? error.name : '';
  if (name === 'NotAllowedError') {
    return 'Izin kamera ditolak. Izinkan akses kamera di browser.';
  }
  if (name === 'NotFoundError' || name === 'OverconstrainedError') {
    return 'Kamera tidak ditemukan.';
  }
  if (name === 'NotReadableError') {
    return 'Kamera sedang dipakai aplikasi lain.';
  }
  if (typeof navigator !== 'undefined' && !navigator.mediaDevices) {
    return 'Browser memblokir kamera. Buka lewat https atau localhost.';
  }
  return 'Kamera gagal dinyalakan.';
}
