import { Config } from "@remotion/cli/config";

// PNG frames: JPEG (default quality 80) visibly softened footage and text edges.
Config.setVideoImageFormat("png");
Config.setOverwriteOutput(true);
// x264 on CPU (this container has no GPU). CRF 18 = visually lossless for delivery.
Config.setCodec("h264");
Config.setCrf(18);
Config.setPixelFormat("yuv420p");
Config.setColorSpace("bt709");
