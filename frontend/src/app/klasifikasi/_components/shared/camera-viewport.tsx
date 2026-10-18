'use client';

import {
  useEffect,
  useRef,
  useState,
  type CSSProperties,
  type ReactNode,
} from 'react';
import type { ClassificationSession } from '../../_hooks/use-classification-session';
import classes from './shared.module.css';

interface ICameraViewportProps {
  session: ClassificationSession;
  children?: ReactNode;
}

export function CameraViewport({ session, children }: ICameraViewportProps) {
  const { videoRef, frameSize, error } = session;
  const containerRef = useRef<HTMLDivElement>(null);
  const [frameStyle, setFrameStyle] = useState<CSSProperties | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container || !frameSize) {
      return undefined;
    }

    const observer = new ResizeObserver(() => {
      const { clientWidth, clientHeight } = container;
      const scale = Math.min(
        clientWidth / frameSize.width,
        clientHeight / frameSize.height
      );
      const width = frameSize.width * scale;
      const height = frameSize.height * scale;
      setFrameStyle({
        left: (clientWidth - width) / 2,
        top: (clientHeight - height) / 2,
        width,
        height,
      });
    });
    observer.observe(container);
    return () => observer.disconnect();
  }, [frameSize]);

  return (
    <div ref={containerRef} className={classes.viewport}>
      <div
        className={classes.viewportFrame}
        style={frameSize && frameStyle ? frameStyle : { inset: 0 }}
      >
        <video ref={videoRef} className={classes.video} muted playsInline />
        {frameSize && children}
      </div>
      {error && <p className={classes.notice}>{error}</p>}
    </div>
  );
}
