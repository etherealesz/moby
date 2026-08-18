# API Library

This directory contains the API client library for interacting with various services. It is designed to be extensible, allowing you to easily add new services as needed.

## Guide

To use the API library within this template, follow the instructions below.

- Add service base url across all `<project-root>/.env` files, example:
  ```
  # Base URL
  NEXT_PUBLIC_SERVICE_NAME_BASE_URL = "https://service-name/"
  ```
- Add the service to the API client library
  - Open `<project-root>/src/lib/api/<protocol>/client.ts`
  - Add the service configuration to the `<protocol>Client` map, e.g., `httpClient`
  - For more information, refer to the comments ontop of `<protocol>Client` variable, within the `client.ts` file.
- Use the API client in your application
  - Import the API client where needed
    Example for http protocol:

    ```typescript
    import { httpClient } from 'src/lib/api/client/client';

    // Example usage
    const fetchData = async () => {
      try {
        const response = await httpClient.serviceName.get('/endpoint');
        console.log(response.data);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };
    ```
