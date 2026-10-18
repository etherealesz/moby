'use client';

import { useEffect, useRef, useState } from 'react';
import { notifications } from '@mantine/notifications';
import { CONFIDENCE_THRESHOLD, getCategory } from '@/app/_data/categories';
import { useGeolocation } from '@/app/_hooks/use-geolocation';
import type { IDetection, IRouteResult } from '@/app/_models/moby';
import { fetchRoute } from '@/app/_services/route';
import {
  CameraController,
  describeCameraError,
} from '../_services/camera-controller';
import {
  CLASSIFY_WS_URL,
  describeServerError,
  toDetections,
  type IClassifyMessage,
  type ITrackHistory,
} from '../_services/classify-stream';

const RETRY_DELAY_MS = 1000;
const FRAME_INTERVAL_MS = 200;

interface IFrameSize {
  width: number;
  height: number;
}

export function useClassificationSession() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const controllerRef = useRef<CameraController | null>(null);
  const historyRef = useRef(new Map<number, ITrackHistory>());

  const [cameraActive, setCameraActive] = useState(false);
  const [deviceId, setDeviceId] = useState<string | null>(null);
  const [showBoxes, setShowBoxes] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detections, setDetections] = useState<IDetection[]>([]);
  const [frameSize, setFrameSize] = useState<IFrameSize | null>(null);
  const [latencyMs, setLatencyMs] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const video = videoRef.current;
    if (!cameraActive || !video) {
      return undefined;
    }

    const controller = new CameraController(video);
    const history = historyRef.current;
    controllerRef.current = controller;
    let socket: WebSocket | null = null;
    let timer: ReturnType<typeof setTimeout> | undefined;
    let cancelled = false;
    let sentAt = 0;

    const sendFrame = async () => {
      if (cancelled || socket?.readyState !== WebSocket.OPEN) {
        return;
      }
      try {
        const frame = await controller.captureFrame();
        if (!cancelled && socket.readyState === WebSocket.OPEN) {
          sentAt = performance.now();
          socket.send(frame);
        }
      } catch {
        timer = setTimeout(sendFrame, RETRY_DELAY_MS);
      }
    };

    const scheduleNextFrame = () => {
      const elapsed = performance.now() - sentAt;
      timer = setTimeout(sendFrame, Math.max(0, FRAME_INTERVAL_MS - elapsed));
    };

    const connect = () => {
      socket = new WebSocket(CLASSIFY_WS_URL);
      socket.onopen = () => void sendFrame();
      socket.onmessage = (event: MessageEvent<string>) => {
        const message = JSON.parse(event.data) as IClassifyMessage;
        if (message.error) {
          setError(describeServerError(message.error.message));
          timer = setTimeout(sendFrame, RETRY_DELAY_MS);
          return;
        }
        if (message.data) {
          setError(null);
          setDetections(toDetections(message.data, history));
          setLatencyMs(message.data.total_time_ms);
        }
        scheduleNextFrame();
      };
      socket.onclose = () => {
        if (!cancelled) {
          setError('Tidak terhubung ke server. Mencoba lagi…');
          timer = setTimeout(connect, RETRY_DELAY_MS);
        }
      };
    };

    controller
      .startStream(deviceId)
      .then(() => {
        if (cancelled) {
          controller.stopStream();
          return;
        }
        setFrameSize(controller.frameSize);
        connect();
      })
      .catch((cause: unknown) => {
        if (!cancelled) {
          setError(describeCameraError(cause));
          setCameraActive(false);
        }
      });

    return () => {
      cancelled = true;
      clearTimeout(timer);
      if (socket) {
        socket.onclose = null;
        socket.close();
      }
      controller.stopStream();
      controllerRef.current = null;
      history.clear();
      setDetections([]);
      setFrameSize(null);
      setLatencyMs(null);
    };
  }, [cameraActive, deviceId]);

  const switchCamera = async () => {
    const devices = (await navigator.mediaDevices.enumerateDevices()).filter(
      (device) => device.kind === 'videoinput'
    );
    if (devices.length < 2) {
      notifications.show({ message: 'Hanya ada satu kamera yang tersedia.' });
      return;
    }
    const currentIndex = devices.findIndex(
      (device) => device.deviceId === controllerRef.current?.deviceId
    );
    setDeviceId(devices[(currentIndex + 1) % devices.length].deviceId);
  };

  const selected =
    detections.find((item) => item.id === selectedId) ?? detections[0] ?? null;
  const selectedIndex = selected ? detections.indexOf(selected) : -1;
  const isConfident = !!selected && selected.confidence >= CONFIDENCE_THRESHOLD;
  const selectedCategoryName = isConfident ? selected.category : null;

  const geo = useGeolocation(!!selectedCategoryName);
  const userPosition = geo.fix?.position ?? null;
  const nearestKey =
    userPosition && selectedCategoryName
      ? `${userPosition.join(',')}|${selectedCategoryName}`
      : null;
  const [nearest, setNearest] = useState<{
    key: string;
    route: IRouteResult | null;
  } | null>(null);

  useEffect(() => {
    if (!nearestKey || !userPosition || !selectedCategoryName) {
      return undefined;
    }
    const controller = new AbortController();
    fetchRoute(
      { start: userPosition, category: selectedCategoryName, network: 'walk' },
      controller.signal
    )
      .then(({ route }) => setNearest({ key: nearestKey, route }))
      .catch(() => {
        if (!controller.signal.aborted) {
          setNearest({ key: nearestKey, route: null });
        }
      });
    return () => controller.abort();
  }, [nearestKey]);

  const nearestRoute = nearest?.key === nearestKey ? nearest.route : null;

  return {
    videoRef,
    cameraActive,
    toggleCamera: () => {
      setError(null);
      setCameraActive((value) => !value);
    },
    switchCamera,
    showBoxes,
    toggleBoxes: () => setShowBoxes((value) => !value),
    frameSize,
    latencyMs,
    error,
    detections,
    selectedId: selected?.id ?? null,
    setSelectedId,
    selected,
    selectedIndex,
    selectedCategory: selected ? getCategory(selected.category) : null,
    isConfident,
    nearestRoute,
  };
}

export type ClassificationSession = ReturnType<typeof useClassificationSession>;
