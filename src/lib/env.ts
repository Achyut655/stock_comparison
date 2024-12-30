import { createEnv } from "@t3-oss/env-nextjs";
import { z } from "zod";

export const env = createEnv({
  server: {
    BREEZE_API_KEY: z.string().min(1),
    BREEZE_SECRET_KEY: z.string().min(1),
  },
  client: {},
  experimental__runtimeEnv: {},
});
