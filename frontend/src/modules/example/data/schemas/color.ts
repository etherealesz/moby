import { z } from 'zod';

export const SColor = z
  .object({
    hex: z.string(),
    rgb: z.string(),
    hsl: z.string(),
  })
  .transform((data) => {
    const { rgb, hsl, ...rest } = data;

    const rgbValue = rgb.match(/\d+(\.\d+)?/g)?.map(Number) || [];
    const hslValue = hsl.match(/\d+(\.\d+)?/g)?.map(Number) || [];

    return {
      rgb: {
        r: rgbValue[0] || 0,
        g: rgbValue[1] || 0,
        b: rgbValue[2] || 0,
      },
      hsl: {
        h: hslValue[0] || 0,
        s: hslValue[1] || 0,
        l: hslValue[2] || 0,
      },
      ...rest,
    };
  });
export type TColor = z.infer<typeof SColor>;
