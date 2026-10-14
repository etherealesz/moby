'use client';

import { useMemo, useState } from 'react';
import { CONFIDENCE_THRESHOLD, getCategory } from '@/app/_data/categories';
import { DUMMY_DETECTIONS } from '@/app/_data/detections';
import { findNearestRoute } from '@/app/_data/dummy-route';
import { DUMMY_USER_POSITION } from '@/app/_data/facilities';

export function useClassificationSession() {
  const [cameraActive, setCameraActive] = useState(true);
  const [showBoxes, setShowBoxes] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(
    DUMMY_DETECTIONS[0]?.id ?? null
  );

  const detections = cameraActive ? DUMMY_DETECTIONS : [];
  const selectedIndex = detections.findIndex((item) => item.id === selectedId);
  const selected = selectedIndex >= 0 ? detections[selectedIndex] : null;
  const isConfident = !!selected && selected.confidence >= CONFIDENCE_THRESHOLD;

  const nearestRoute = useMemo(
    () =>
      selected && isConfident
        ? findNearestRoute(selected.category, DUMMY_USER_POSITION)
        : null,
    [selected, isConfident]
  );

  return {
    cameraActive,
    toggleCamera: () => setCameraActive((value) => !value),
    showBoxes,
    toggleBoxes: () => setShowBoxes((value) => !value),
    detections,
    selectedId,
    setSelectedId,
    selected,
    selectedIndex,
    selectedCategory: selected ? getCategory(selected.category) : null,
    isConfident,
    nearestRoute,
  };
}

export type ClassificationSession = ReturnType<typeof useClassificationSession>;
