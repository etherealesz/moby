import { ApplicationError } from '@/src/shared/errors';

export class GetRandomColorFailedError extends ApplicationError {
  constructor() {
    super('Error', 'Failed to get a random color.');
  }
}
