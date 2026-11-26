import { test, expect } from '../../frontend/node_modules/@playwright/test';

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
  await page.screenshot({ path: '../docs/evidence/gd01/browser-preview.png' });
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
