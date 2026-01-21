/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    if (!process.env.API_PROXY_TARGET) {
      throw new Error('API_PROXY_TARGET is not defined');
    }

    return [
      {
        source: '/api/:path*',
        destination: `${process.env.API_PROXY_TARGET}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
