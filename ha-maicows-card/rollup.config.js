import resolve from "@rollup/plugin-node-resolve";
import terser from "@rollup/plugin-terser";

export default {
    input: "src/maico-vmc-card.js",
    output: {
        file: "dist/maico-vmc-card.js",
        format: "es",
    },
    plugins: [
        resolve(),
        terser({
            format: {
                comments: false,
            },
        }),
    ],
};
