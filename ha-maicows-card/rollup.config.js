import resolve from "@rollup/plugin-node-resolve";
import terser from "@rollup/plugin-terser";

export default {
    input: "src/ha-maicows-card.js",
    output: {
        file: "dist/ha-maicows-card.js",
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
