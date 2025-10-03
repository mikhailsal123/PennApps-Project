import type { NextConfig } from "next";

const nextConfig: NextConfig = {
    output: 'export',
    trailingSlash: true,
    images: {
        unoptimized: true
    },
    assetPrefix: process.env.NODE_ENV === 'production' ? '/PennApps-Project' : '',
    basePath: process.env.NODE_ENV === 'production' ? '/PennApps-Project' : '',
};
  
export default nextConfig;
  
  
  
  
  