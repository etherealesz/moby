/**
 * Service to retrieve current device geolocation coordinates
 */
export interface IGeoLocationResult {
  latitude: number;
  longitude: number;
}

export const DEFAULT_JAKARTA_COORDS: IGeoLocationResult = {
  latitude: -6.2088,
  longitude: 106.8456,
};

export async function getCurrentLocation(): Promise<IGeoLocationResult> {
  return new Promise((resolve, reject) => {
    if (typeof window === 'undefined' || !navigator.geolocation) {
      return reject(new Error('Geolocation tidak didukung oleh peramban ini.'));
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        });
      },
      (error) => {
        reject(error);
      },
      { timeout: 8000, enableHighAccuracy: true }
    );
  });
}
