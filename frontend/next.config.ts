import type { NextConfig } from "next";

const nextConfig: NextConfig = {
    output: 'export',
    trailingSlash: true,
    images: {
        unoptimized: true
    },
    // Remove assetPrefix and basePath for Render deployment
    // assetPrefix: process.env.NODE_ENV === 'production' ? '/PennApps-Project' : '',
    // basePath: process.env.NODE_ENV === 'production' ? '/PennApps-Project' : '',
};
  
export default nextConfig;
  
  
  
  
  