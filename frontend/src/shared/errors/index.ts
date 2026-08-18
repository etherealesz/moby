export class ApplicationError extends Error {
  public readonly name: string;

  constructor(name: string, message: string) {
    super(message);
    this.name = name;

    Object.setPrototypeOf(this, ApplicationError.prototype);
  }
}

export class ParsingDataError extends ApplicationError {
  constructor() {
    super('Error', 'Gagal memproses data, silahkan coba beberapa saat lagi');
  }
}

export class NetworkError extends ApplicationError {
  constructor() {
    super(
      'Error',
      'Terjadi kesalahan jaringan, silahkan periksa koneksi internet anda'
    );
  }
}
