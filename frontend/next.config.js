/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true, // Good practice to include this
  env: {
    NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
  },
  async rewrites() {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`, // ✅ avoid using undefined here
      },
    ];
  },
};

module.exports = nextConfig;
