/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  eslint: {
    dirs: ["app", "components", "lib"]
  }
};

export default nextConfig;
