/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  transpilePackages: ['@material/web', '@material/material-color-utilities'],
  experimental: {
    serverComponentsExternalPackages: [],
  },
}

module.exports = nextConfig
