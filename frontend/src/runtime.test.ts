import { describe, expect, it } from 'vitest';
import { portraitSize } from './runtime';

describe('9:16 logical output', () => {
  it.each([[1920, 1080], [1080, 1920], [320, 800]])('fits %i × %i', (w, h) => {
    const size = portraitSize(w, h);
    expect(size.width / size.height).toBeCloseTo(9 / 16);
    expect(size.width).toBeLessThanOrEqual(w);
    expect(size.height).toBeLessThanOrEqual(h);
  });
});
