import { NextConfig } from 'next';
import bundleAnalyzer from '@next/bundle-analyzer';

const config = {
  inProductionAppEnvironment: process.env.APP_ENV === 'production',
  inBuildEnvironment: process.env.NODE_ENV === 'production',
  usingAnalyze: process.env.ANALYZE === 'true',
};

const distDir = config.inBuildEnvironment
  ? `./dist/${process.env.APP_ENV}`
  : '.next';

const withBundleAnalyzer = bundleAnalyzer({
  enabled: config.usingAnalyze,
});

const nextConfig: NextConfig = {
  distDir,
  output: 'standalone',
  experimental: {
    authInterrupts: true,
    optimizePackageImports: ['@mantine/core', '@mantine/hooks'],
  },
  devIndicators: false,
  allowedDevOrigins: ['*.trycloudflare.com'],
};

export default withBundleAnalyzer(nextConfig);
