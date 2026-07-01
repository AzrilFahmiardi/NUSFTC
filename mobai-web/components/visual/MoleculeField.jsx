"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { useMemo, useRef } from "react";
import * as THREE from "three";

// Low-density drifting molecular network used as a subtle hero backdrop.
function Network({ count = 44 }) {
  const group = useRef();
  const { positions, linePositions } = useMemo(() => {
    const pts = [];
    for (let i = 0; i < count; i++) {
      pts.push(new THREE.Vector3((Math.random() - 0.5) * 9.5, (Math.random() - 0.5) * 6, (Math.random() - 0.5) * 5));
    }
    const pos = new Float32Array(count * 3);
    pts.forEach((p, i) => {
      pos[i * 3] = p.x;
      pos[i * 3 + 1] = p.y;
      pos[i * 3 + 2] = p.z;
    });
    const lines = [];
    for (let i = 0; i < count; i++) {
      for (let j = i + 1; j < count; j++) {
        if (pts[i].distanceTo(pts[j]) < 2.1) {
          lines.push(pts[i].x, pts[i].y, pts[i].z, pts[j].x, pts[j].y, pts[j].z);
        }
      }
    }
    return { positions: pos, linePositions: new Float32Array(lines) };
  }, [count]);

  useFrame((_, delta) => {
    if (group.current) {
      group.current.rotation.y += delta * 0.05;
      group.current.rotation.x += delta * 0.012;
    }
  });

  return (
    <group ref={group}>
      <points>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" array={positions} count={positions.length / 3} itemSize={3} />
        </bufferGeometry>
        <pointsMaterial size={0.13} color="#d9bd79" sizeAttenuation transparent opacity={0.9} />
      </points>
      <lineSegments>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" array={linePositions} count={linePositions.length / 3} itemSize={3} />
        </bufferGeometry>
        <lineBasicMaterial color="#8bb391" transparent opacity={0.2} />
      </lineSegments>
    </group>
  );
}

export default function MoleculeField() {
  return (
    <Canvas camera={{ position: [0, 0, 9], fov: 60 }} dpr={[1, 1.8]} gl={{ antialias: true, alpha: true }} style={{ width: "100%", height: "100%" }}>
      <Network />
    </Canvas>
  );
}
