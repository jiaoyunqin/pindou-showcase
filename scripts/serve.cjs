// Standalone, build-free preview. Only page files and prepared WebP assets
// are served; original screenshots and planning files stay outside the route.
const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const port = Number(process.argv[2] || 4174);
const pageFiles = new Set([
  "index.html",
  "styles.css",
  "styles-sections.css",
  "styles-outcomes.css",
  "styles-responsive.css",
  "interactions.js",
]);
const contentTypes = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".webp": "image/webp",
};

if (!Number.isInteger(port) || port < 1 || port > 65535) {
  console.error("Please provide a valid port, e.g. node scripts/serve.cjs 4174");
  process.exit(1);
}

const server = http.createServer((request, response) => {
  if (request.method !== "GET" && request.method !== "HEAD") {
    response.writeHead(405, { Allow: "GET, HEAD" }).end();
    return;
  }

  const queryStart = request.url.indexOf("?");
  const rawPath = queryStart === -1 ? request.url : request.url.slice(0, queryStart);
  let decodedPath;
  try {
    decodedPath = decodeURIComponent(rawPath);
  } catch {
    response.writeHead(400).end("Bad request");
    return;
  }

  const segments = decodedPath.split("/");
  if (!decodedPath.startsWith("/") ||
      decodedPath.includes("\\") ||
      decodedPath.includes("\0") ||
      segments.includes("..")) {
    response.writeHead(404).end("Not found");
    return;
  }

  const requestedFile = decodedPath.slice(1) || "index.html";
  const file = requestedFile === "favicon.ico" ? "assets/blueprint.webp" : requestedFile;
  if (requestedFile !== "favicon.ico" &&
      !pageFiles.has(requestedFile) &&
      !/^assets\/[a-z0-9-]+\.webp$/.test(requestedFile)) {
    response.writeHead(404).end("Not found");
    return;
  }
  fs.readFile(path.join(root, file), (error, data) => {
    if (error) {
      response.writeHead(error.code === "ENOENT" ? 404 : 500).end("File unavailable");
      return;
    }
    response.writeHead(200, {
      "Content-Type": contentTypes[path.extname(file)],
      "Cache-Control": "no-cache",
      "X-Content-Type-Options": "nosniff",
    });
    response.end(request.method === "HEAD" ? undefined : data);
  });
});

server.on("error", (error) => {
  console.error(error.code === "EADDRINUSE" ? `Port ${port} is busy. Pass another port as the first argument.` : error.message);
  process.exitCode = 1;
});
server.listen(port, "127.0.0.1", () => {
  console.log(`豆拼拼豆推介页: http://127.0.0.1:${port}/`);
});
