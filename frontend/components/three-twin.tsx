"use client";

import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';

interface ThreeTwinProps {
  healthScore: number;
  alertActive: boolean;
  thermalOffset: number;
  vibrationLevel: number;
}

export default function ThreeDigitalTwin({
  healthScore,
  alertActive,
  thermalOffset,
  vibrationLevel
}: ThreeTwinProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const width = containerRef.current.clientWidth;
    const height = containerRef.current.clientHeight;

    // 1. Create Scene, Camera, and WebGLRenderer
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x020617); // Slate-950

    const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
    camera.position.set(0, 3, 7);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    
    // Clear container and append renderer canvas
    containerRef.current.innerHTML = '';
    containerRef.current.appendChild(renderer.domElement);

    // 2. Add Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.35);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0x00E5FF, 1.2); // Cyan glow light
    dirLight1.position.set(5, 5, 5);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(alertActive ? 0xFF1744 : 0x00E676, 0.8); // Crimson/Green light
    dirLight2.position.set(-5, -5, -5);
    scene.add(dirLight2);

    // 3. Construct Industrial Spindle machinery using Primitive Geometries
    const machineGroup = new THREE.Group();
    scene.add(machineGroup);

    // Main Engine casing block
    const casingGeo = new THREE.CylinderGeometry(1.6, 1.8, 3.5, 32);
    const casingMat = new THREE.MeshStandardMaterial({
      color: alertActive ? 0x2d0b11 : 0x0f172a, // Red-ish tint on active alert
      roughness: 0.45,
      metalness: 0.8,
      transparent: true,
      opacity: 0.9
    });
    const casing = new THREE.Mesh(casingGeo, casingMat);
    casing.rotation.x = Math.PI / 2;
    machineGroup.add(casing);

    // Rotating spindle core shaft
    const shaftGeo = new THREE.CylinderGeometry(0.5, 0.5, 4.8, 16);
    const shaftMat = new THREE.MeshStandardMaterial({
      color: 0x94a3b8,
      roughness: 0.15,
      metalness: 0.95
    });
    const shaft = new THREE.Mesh(shaftGeo, shaftMat);
    shaft.rotation.x = Math.PI / 2;
    machineGroup.add(shaft);

    // Dynamic rotating flywheel coupling rings
    const wheelGeo = new THREE.TorusGeometry(1.2, 0.15, 12, 48);
    const wheelMat = new THREE.MeshStandardMaterial({
      color: 0x00E5FF, // glowing cyan rings
      roughness: 0.2,
      metalness: 0.9
    });
    const wheel = new THREE.Mesh(wheelGeo, wheelMat);
    wheel.position.z = 1.6;
    machineGroup.add(wheel);

    // Thermal Hotspots (glowing red mesh indicator overlay)
    const heatGeo = new THREE.SphereGeometry(1.65, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2);
    const heatColor = new THREE.Color().setHSL(0.0, 1.0, 0.5); // Crimson
    const heatMat = new THREE.MeshBasicMaterial({
      color: heatColor,
      transparent: true,
      opacity: Math.min(0.85, (thermalOffset / 50.0) * 0.7), // more hot = more opaque red glow
      wireframe: true
    });
    const heatOverlay = new THREE.Mesh(heatGeo, heatMat);
    heatOverlay.rotation.x = -Math.PI / 2;
    machineGroup.add(heatOverlay);

    // 4. Particle Field for vibrational and kinetic waves
    const particleCount = 200;
    const particleGeo = new THREE.BufferGeometry();
    const particlePositions = new Float32Array(particleCount * 3);
    const particleSpeeds: number[] = [];

    for (let i = 0; i < particleCount * 3; i += 3) {
      // Circle coordinates
      const angle = Math.random() * Math.PI * 2;
      const radius = 1.8 + Math.random() * 0.8;
      particlePositions[i] = Math.cos(angle) * radius;
      particlePositions[i + 1] = Math.sin(angle) * radius;
      particlePositions[i + 2] = (Math.random() - 0.5) * 4.0;
      particleSpeeds.push(0.01 + Math.random() * 0.03);
    }

    particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
    const particleMat = new THREE.PointsMaterial({
      color: alertActive ? 0xFF1744 : 0x00E676,
      size: 0.08,
      transparent: true,
      opacity: 0.8
    });
    const particles = new THREE.Points(particleGeo, particleMat);
    machineGroup.add(particles);

    // 5. Animation Loop
    let animationId: number;
    let rotationSpeed = 0.03;

    // Slow down rotation if health score drops, speed up with RPM (simulated kinetic)
    if (healthScore < 50) rotationSpeed = 0.005;

    const animate = () => {
      animationId = requestAnimationFrame(animate);

      // Rotate flywheel and central shaft
      wheel.rotation.z += rotationSpeed;
      shaft.rotation.z += rotationSpeed;

      // Inject vibrational jitter based on vibration level
      if (vibrationLevel > 1.2) {
        const jitter = (vibrationLevel - 1.2) * 0.015;
        machineGroup.position.set(
          (Math.random() - 0.5) * jitter,
          (Math.random() - 0.5) * jitter,
          (Math.random() - 0.5) * jitter
        );
      } else {
        machineGroup.position.set(0, 0, 0);
      }

      // Rotate entire assembly slowly on camera axis for full visibility
      machineGroup.rotation.y += 0.004;

      // Animate particle flow
      const positions = particles.geometry.attributes.position.array as Float32Array;
      for (let i = 0; i < particleCount * 3; i += 3) {
        positions[i + 2] += particleSpeeds[i / 3] * (vibrationLevel * 1.5);
        // Reset when flowing past coupling limit
        if (positions[i + 2] > 2.5) {
          positions[i + 2] = -2.5;
        }
      }
      particles.geometry.attributes.position.needsUpdate = true;

      renderer.render(scene, camera);
    };
    animate();

    // 6. Handle Container Resize
    const handleResize = () => {
      if (!containerRef.current) return;
      const w = containerRef.current.clientWidth;
      const h = containerRef.current.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener('resize', handleResize);
      renderer.dispose();
    };

  }, [healthScore, alertActive, thermalOffset, vibrationLevel]);

  return <div ref={containerRef} className="w-full h-full min-h-[350px] relative rounded-2xl overflow-hidden" />;
}
