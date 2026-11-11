import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  cacheComponents: true,
  // The dev badge sits on top of the phone tab bar; errors are still surfaced.
  devIndicators: false,
  partialPrefetching: true,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
