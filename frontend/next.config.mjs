/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  async rewrites() {
    const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

    if (!BACKEND_URL) {
      console.warn(
        "NEXT_PUBLIC_BACKEND_URL não definido. Rewrites de API podem falhar."
      );
    }

    return [
      {
        source: "/api/:path*",
        destination: `${BACKEND_URL}/:path*`, // URL do backend no Render
      },
    ];
  },
};

export default nextConfig;
