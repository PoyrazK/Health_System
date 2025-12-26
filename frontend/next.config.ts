import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: false, // Disabled to prevent double-mounting issues with WebSockets
};

export default nextConfig;
