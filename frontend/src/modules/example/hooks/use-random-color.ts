import useSWR from 'swr';
import { colorService } from '../services';

const execute = () => {
  const response = colorService.getRandomColor();
  return response;
};

export function useRandomColor() {
  const fetchKey = 'random-color';
  const { data, error, isLoading } = useSWR(fetchKey, execute);

  return {
    data,
    error,
    isLoading,
  };
}
