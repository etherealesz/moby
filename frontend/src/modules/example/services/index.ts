import { AxiosResponse, HttpStatusCode } from 'axios';
import httpClient from '@/src/lib/api/http/client';
import { safeParseZodObject } from '@/src/shared/utils/parser';
import { SColor, TColor } from '../data/schemas/color';
import { GetRandomColorFailedError } from '../errors';

export const colorService = {
  getRandomColor: async () => {
    const response: AxiosResponse<TColor> | undefined =
      await httpClient.xColors.get('/random');
    if (response?.status === HttpStatusCode.Ok) {
      const responseData = safeParseZodObject<TColor>(SColor, response.data);
      return responseData;
    }

    throw new GetRandomColorFailedError();
  },
};
