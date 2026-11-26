import * as THREE from 'three';

export function portraitSize(width: number, height: number) {
  const w = Math.max(1, Math.min(width, height * 9 / 16));
  return { width: w, height: w * 16 / 9 };
}

export class FoundationRuntime {
  readonly scene = new THREE.Scene();
  readonly camera = new THREE.PerspectiveCamera(40, 9 / 16, 0.1, 100);
  readonly character = new THREE.Group();
  private renderer?: THREE.WebGLRenderer;
  private observer?: ResizeObserver;
  private frame = 0;
  private disposed = false;
  private frames = 0;
  private state = 'initializing';
  private geometries = new Set<THREE.BufferGeometry>();
  private materials = new Set<THREE.Material>();
  private released = 0;

  constructor(private host: HTMLElement, private onError: (message: string) => void) {}

  start() {
    try {
      this.renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      this.renderer.setClearColor('#161925');
      this.renderer.domElement.addEventListener('webglcontextlost', this.contextLost);
      this.host.append(this.renderer.domElement);
      this.camera.position.set(4, 3.7, 7);
      this.camera.lookAt(0, 1, 0);
      this.scene.add(new THREE.AmbientLight(0xffffff, 1.8));
      const light = new THREE.DirectionalLight(0xd9ccff, 4);
      light.position.set(3, 6, 4);
      this.scene.add(light);
      const mesh = (geometry: THREE.BufferGeometry, color: string) => {
        const material = new THREE.MeshStandardMaterial({ color, roughness: 0.6 });
        this.geometries.add(geometry); this.materials.add(material);
        return new THREE.Mesh(geometry, material);
      };
      const ground = mesh(new THREE.CylinderGeometry(2.8, 3, .2, 48), '#29233f');
      ground.position.y = -.15;
      this.scene.add(ground);
      const grid = new THREE.GridHelper(6, 12, '#8b5cf6', '#353146');
      this.geometries.add(grid.geometry);
      (Array.isArray(grid.material) ? grid.material : [grid.material]).forEach(m => this.materials.add(m));
      this.scene.add(grid);
      const body = mesh(new THREE.CapsuleGeometry(.35, .65, 4, 12), '#8b5cf6');
      body.position.y = 1.1;
      const head = mesh(new THREE.SphereGeometry(.35, 24, 16), '#ddd6fe');
      head.position.y = 1.95;
      this.character.add(body, head);
      for (const x of [-.23, .23]) {
        const leg = mesh(new THREE.BoxGeometry(.24, .6, .27), '#695399');
        leg.position.set(x, .3, 0); this.character.add(leg);
        const arm = mesh(new THREE.BoxGeometry(.2, .7, .2), '#a78bfa');
        arm.position.set(x * 2.4, 1.15, 0); this.character.add(arm);
      }
      this.scene.add(this.character);
      this.observer = new ResizeObserver(this.resize);
      this.observer.observe(this.host);
      this.resize(); this.state = 'running';
      this.frame = requestAnimationFrame(this.animate);
    } catch {
      this.fail('WebGL unavailable. Mở preview bằng trình duyệt hỗ trợ WebGL.');
    }
  }

  private resize = () => {
    if (this.disposed || !this.renderer) return;
    const size = portraitSize(this.host.clientWidth, this.host.clientHeight);
    this.renderer.setSize(size.width, size.height, false);
    this.camera.aspect = 9 / 16;
    this.camera.updateProjectionMatrix();
  };

  private animate = (time: number) => {
    if (this.disposed || !this.renderer) return;
    try {
      this.character.rotation.y = time * .0004;
      this.character.position.y = Math.sin(time * .0015) * .06;
      this.renderer.render(this.scene, this.camera);
      this.frames++;
      this.frame = requestAnimationFrame(this.animate);
    } catch { this.fail('Rendering failed. Tải lại preview để thử lại.'); }
  };

  private contextLost = (event: Event) => {
    event.preventDefault();
    this.fail('WebGL context lost. Tải lại preview để khôi phục.');
  };

  private fail(message: string) {
    this.dispose(); this.state = 'error'; this.onError(message);
  }

  diagnostics() {
    const gl = this.renderer?.getContext();
    const debug = gl?.getExtension('WEBGL_debug_renderer_info');
    return { state: this.state, frames: this.frames, aspect: this.camera.aspect,
      width: this.renderer?.domElement.width, height: this.renderer?.domElement.height,
      renderer: gl?.getParameter(gl.RENDERER), webglVersion: gl?.getParameter(gl.VERSION),
      gpuRenderer: debug ? gl?.getParameter(debug.UNMASKED_RENDERER_WEBGL) : 'unavailable',
      gpuGeometries: this.renderer?.info.memory.geometries ?? 0,
      drawCalls: this.renderer?.info.render.calls ?? 0, released: this.released,
      resources: this.geometries.size + this.materials.size, disposed: this.disposed };
  }

  dispose() {
    if (this.disposed) return;
    this.disposed = true;
    cancelAnimationFrame(this.frame);
    this.observer?.disconnect();
    this.renderer?.domElement.removeEventListener('webglcontextlost', this.contextLost);
    this.geometries.forEach(g => { g.dispose(); this.released++; });
    this.materials.forEach(m => { m.dispose(); this.released++; });
    this.renderer?.dispose();
    this.renderer?.forceContextLoss();
    this.renderer?.domElement.remove();
    this.scene.clear();
    this.state = 'disposed';
  }
}
