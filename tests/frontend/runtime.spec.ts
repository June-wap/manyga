import { test, expect } from '../../frontend/node_modules/@playwright/test';
import { join } from 'node:path';

const evidenceDir = process.env.LGS_EVIDENCE_DIR ?? '../docs/evidence/gd01';

test('real WebGL, rotation, 9:16, resize and disposal', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  await page.goto('/');
  await page.waitForFunction(() => (window as any).foundation?.diagnostics().frames > 4);
  const before = await page.evaluate(() => ({ diagnostic: (window as any).foundation.diagnostics(),
    rotation: (window as any).foundation.character.rotation.y }));
  expect(before.diagnostic.state).toBe('running');
  expect(before.diagnostic.drawCalls).toBeGreaterThan(0);
  expect(before.diagnostic.webglVersion).toContain('WebGL');
  expect(before.diagnostic.width).toBe(1080);
  expect(before.diagnostic.height).toBe(1920);
  // Read actual framebuffer pixels; a canvas and animation counter alone are insufficient.
  const colors = await page.evaluate(() => {
    const canvas = document.querySelector('canvas')!;
    const gl = canvas.getContext('webgl2')!;
    const pixels = new Uint8Array(4 * 1080 * 1920);
    gl.readPixels(0, 0, 1080, 1920, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
    const values = new Set<string>();
    for (let i = 0; i < pixels.length; i += 400) values.add(`${pixels[i]},${pixels[i+1]},${pixels[i+2]}`);
    return values.size;
  });
  expect(colors).toBeGreaterThan(10);
  await page.screenshot({ path: join(evidenceDir, 'browser-preview.png') });
  await page.setViewportSize({ width: 1280, height: 800 });
  await expect.poll(async () => page.evaluate(() => {
    const d = (window as any).foundation.diagnostics(); return d.width / d.height;
  })).toBeCloseTo(9 / 16, 2);
  const after = await page.evaluate(() => (window as any).foundation.character.rotation.y);
  expect(after).not.toBe(before.rotation);
  const disposed = await page.evaluate(() => {
    const runtime = (window as any).foundation;
    runtime.dispose(); runtime.dispose(); return runtime.diagnostics();
  });
  expect(disposed.state).toBe('disposed');
  expect(disposed.released).toBe(disposed.resources);
  expect(disposed.gpuGeometries).toBe(0);
  await page.waitForTimeout(150);
  expect(await page.evaluate(() => (window as any).foundation.diagnostics().frames)).toBe(disposed.frames);
  expect(await page.locator('canvas').count()).toBe(0);
  expect(errors).toEqual([]);
});

test('WebGL unavailable shows a real error state', async ({ page }) => {
  await page.addInitScript(() => {
    const original = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function(type: string, ...args: any[]) {
      if (type.includes('webgl')) return null;
      return (original as any).call(this, type, ...args);
    } as any;
  });
  await page.goto('/');
  await expect(page.getByRole('alert')).toContainText('WebGL unavailable');
  expect(await page.evaluate(() => (window as any).foundation.diagnostics().state)).toBe('error');
});

test('real context loss stops animation and releases resources', async ({ page }) => {
  await page.goto('/');
  await page.waitForFunction(() => (window as any).foundation?.diagnostics().frames > 2);
  await page.evaluate(() => document.querySelector('canvas')!.getContext('webgl2')!
    .getExtension('WEBGL_lose_context')!.loseContext());
  await expect(page.getByRole('alert')).toContainText('context lost');
  const state = await page.evaluate(() => (window as any).foundation.diagnostics());
  expect(state.disposed).toBe(true);
  expect(state.released).toBe(state.resources);
});

test('static production build renders without dev client or external resources', async ({ page }) => {
  const errors: string[] = [];
  const requests: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  page.on('request', request => requests.push(request.url()));
  await page.goto('http://127.0.0.1:15174');
  await page.waitForFunction(() => (window as any).foundation?.diagnostics().frames > 4);
  const diag = await page.evaluate(() => (window as any).foundation.diagnostics());
  expect(diag.drawCalls).toBeGreaterThan(0);
  expect(diag.width).toBe(1080);
  expect(diag.height).toBe(1920);
  expect(requests.some(url => url.includes('/assets/'))).toBe(true);
  expect(requests.every(url => url.startsWith('http://127.0.0.1:15174/'))).toBe(true);
  expect(requests.some(url => url.includes('@vite/client'))).toBe(false);
  await page.screenshot({ path: join(evidenceDir, 'static-production.png') });
  expect(errors).toEqual([]);
});

test('missing optional GPU debug extension keeps actual WebGL running', async ({ page }) => {
  await page.addInitScript(() => {
    for (const type of [WebGLRenderingContext, WebGL2RenderingContext]) {
      const getExtension = type.prototype.getExtension;
      type.prototype.getExtension = function(name: string) {
        return name === 'WEBGL_debug_renderer_info' ? null : getExtension.call(this, name);
      } as any;
    }
  });
  await page.goto('/');
  await page.waitForFunction(() => (window as any).foundation?.diagnostics().frames > 4);
  const diag = await page.evaluate(() => (window as any).foundation.diagnostics());
  expect(diag.gpuRenderer).toBe('unavailable');
  expect(diag.state).toBe('running');
  expect(diag.drawCalls).toBeGreaterThan(0);
});
