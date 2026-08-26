# MULESHIELD PRO V2 — PHASE 13
# Kubernetes Deployment Architecture

> **Note**: This document assumes the Docker deployment (docker‑compose) is stable and has been validated locally.  The Kubernetes manifests below are provided for development / staging environments only.  They have **not** been tested in a production cluster, and no real secrets are included.

---

## 1. Architecture Overview

```
+-------------------+        +-------------------+        +-------------------+
|   Frontend (NGINX|<----->|   API Gateway      |<----->|   Auth Service    |
|   or Next.js)    |        |   (Flask)          |        +-------------------+
+-------------------+        +-------------------+               |
        |                            |                       |
        |                            |                       |
        v                            v                       v
+-------------------+        +-------------------+        +-------------------+
|   ML Service      |        |   Graph Service   |        |   Case Service    |
|   (Python)        |        |   (Python)        |        |   (Python)        |
+-------------------+        +-------------------+        +-------------------+
        |                            |                       |
        |                            |                       |
        +----------+-----------------+-----------------------+
                   |
                   v
            +--------------+
            |   Kafka      |
            +--------------+
                   |
                   v
            +--------------+
            | PostgreSQL   |
            +--------------+
```

- **Frontend** – Serves the static `index.html` (or runs the Next.js build).  It is exposed via a LoadBalancer/Ingress.
- **API Gateway** – Flask application (`backend/main.py`) handling auth, routing, and health checks.
- **Auth Service** – Embedded in the API gateway (JWT creation/verification).  Separate service could be extracted later.
- **ML Service** – Inference service (`backend/services/ml_service`).
- **Graph Service** – Transaction‑graph calculations (`backend/services/graph_service`).
- **Case Service** – Placeholder for case‑management APIs (currently part of the API gateway but can be split).
- **Kafka** – Event bus for asynchronous processing (e.g., audit events, model‑training triggers).
- **PostgreSQL** – Persistent data store for users, audit logs, model registry.

---

## 2. Kubernetes Manifests (YAML snippets)

All manifests are placed under `k8s/` (you can copy‑paste them into the appropriate files).  They use **Deployments**, **Services**, **ConfigMaps**, and **Secrets**.  Resource limits are conservative for a dev cluster.

### 2.1 Namespace (optional)
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: muleshield-pro-v2
```

### 2.2 Secrets (placeholder – do **not** commit real values)
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: muleshield-secrets
  namespace: muleshield-pro-v2
type: Opaque
stringData:
  JWT_SECRET_KEY: "CHANGE_ME_IN_PRODUCTION"
  POSTGRES_PASSWORD: "CHANGE_ME_IN_PRODUCTION"
```

### 2.3 ConfigMap (environment configuration)
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: muleshield-config
  namespace: muleshield-pro-v2
data:
  # Service URLs – they resolve to the internal ClusterIP services created below
  ML_SERVICE_URL: "http://ml-service:8080"
  GRAPH_SERVICE_URL: "http://graph-service:8081"
  REPORTING_SERVICE_URL: "http://reporting-service:8082"
  # Other tunables
  SERVICE_TIMEOUT: "5"
```

### 2.4 PostgreSQL Deployment & Service
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: muleshield-pro-v2
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:15-alpine
          env:
            - name: POSTGRES_USER
              value: "muleshield"
            - name: POSTGRES_DB
              value: "muleshield_db"
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: muleshield-secrets
                  key: POSTGRES_PASSWORD
          ports:
            - containerPort: 5432
          volumeMounts:
            - name: pgdata
              mountPath: /var/lib/postgresql/data
          resources:
            limits:
              cpu: "500m"
              memory: "512Mi"
            requests:
              cpu: "250m"
              memory: "256Mi"
      volumes:
        - name: pgdata
          emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: muleshield-pro-v2
spec:
  selector:
    app: postgres
  ports:
    - protocol: TCP
      port: 5432
      targetPort: 5432
  clusterIP: None   # headless service for direct DNS resolution
```

### 2.5 Kafka Deployment & Service (single‑node for dev)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kafka
  namespace: muleshield-pro-v2
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kafka
  template:
    metadata:
      labels:
        app: kafka
    spec:
      containers:
        - name: kafka
          image: confluentinc/cp-kafka:7.5.0
          env:
            - name: KAFKA_BROKER_ID
              value: "1"
            - name: KAFKA_ZOOKEEPER_CONNECT
              value: "zookeeper:2181"
            - name: KAFKA_ADVERTISED_LISTENERS
              value: PLAINTEXT://kafka:9092
            - name: KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR
              value: "1"
          ports:
            - containerPort: 9092
          resources:
            limits:
              cpu: "500m"
              memory: "512Mi"
            requests:
              cpu: "250m"
              memory: "256Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: kafka
  namespace: muleshield-pro-v2
spec:
  selector:
    app: kafka
  ports:
    - protocol: TCP
      port: 9092
      targetPort: 9092
```
> *A minimal Zookeeper deployment is omitted for brevity; include it if you intend to run a real Kafka cluster.*

### 2.6 API Gateway Deployment & Service
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: muleshield-pro-v2
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
        - name: api-gateway
          image: muleshield/api-gateway:latest   # build this image from backend/Dockerfile
          envFrom:
            - configMapRef:
                name: muleshield-config
            - secretRef:
                name: muleshield-secrets
          ports:
            - containerPort: 8000
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 15
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 20
          resources:
            limits:
              cpu: "500m"
              memory: "512Mi"
            requests:
              cpu: "250m"
              memory: "256Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
  namespace: muleshield-pro-v2
spec:
  selector:
    app: api-gateway
  ports:
    - protocol: TCP
      port: 8000
      targetPort: 8000
  type: ClusterIP
```

### 2.7 ML Service Deployment & Service
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-service
  namespace: muleshield-pro-v2
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ml-service
  template:
    metadata:
      labels:
        app: ml-service
    spec:
      containers:
        - name: ml-service
          image: muleshield/ml-service:latest   # built from backend/services/ml_service/Dockerfile
          envFrom:
            - configMapRef:
                name: muleshield-config
            - secretRef:
                name: muleshield-secrets
          ports:
            - containerPort: 8080
          readinessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 15
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 20
          resources:
            limits:
              cpu: "1"
              memory: "1Gi"
            requests:
              cpu: "500m"
              memory: "512Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: ml-service
  namespace: muleshield-pro-v2
spec:
  selector:
    app: ml-service
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 8080
  type: ClusterIP
```

### 2.8 Graph Service Deployment & Service
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: graph-service
  namespace: muleshield-pro-v2
spec:
  replicas: 2
  selector:
    matchLabels:
      app: graph-service
  template:
    metadata:
      labels:
        app: graph-service
    spec:
      containers:
        - name: graph-service
          image: muleshield/graph-service:latest   # built from backend/services/graph_service/Dockerfile
          envFrom:
            - configMapRef:
                name: muleshield-config
            - secretRef:
                name: muleshield-secrets
          ports:
            - containerPort: 8081
          readinessProbe:
            httpGet:
              path: /health
              port: 8081
            initialDelaySeconds: 10
            periodSeconds: 15
          livenessProbe:
            httpGet:
              path: /health
              port: 8081
            initialDelaySeconds: 30
            periodSeconds: 20
          resources:
            limits:
              cpu: "500m"
              memory: "512Mi"
            requests:
              cpu: "250m"
              memory: "256Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: graph-service
  namespace: muleshield-pro-v2
spec:
  selector:
    app: graph-service
  ports:
    - protocol: TCP
      port: 8081
      targetPort: 8081
  type: ClusterIP
```

### 2.9 Reporting Service Deployment & Service
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: reporting-service
  namespace: muleshield-pro-v2
spec:
  replicas: 1
  selector:
    matchLabels:
      app: reporting-service
  template:
    metadata:
      labels:
        app: reporting-service
    spec:
      containers:
        - name: reporting-service
          image: muleshield/reporting-service:latest   # built from backend/services/reporting_service/Dockerfile
          envFrom:
            - configMapRef:
                name: muleshield-config
            - secretRef:
                name: muleshield-secrets
          ports:
            - containerPort: 8082
          readinessProbe:
            httpGet:
              path: /health
              port: 8082
            initialDelaySeconds: 10
            periodSeconds: 15
          livenessProbe:
            httpGet:
              path: /health
              port: 8082
            initialDelaySeconds: 30
            periodSeconds: 20
          resources:
            limits:
              cpu: "300m"
              memory: "256Mi"
            requests:
              cpu: "150m"
              memory: "128Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: reporting-service
  namespace: muleshield-pro-v2
spec:
  selector:
    app: reporting-service
  ports:
    - protocol: TCP
      port: 8082
      targetPort: 8082
  type: ClusterIP
```

### 2.10 Frontend Deployment & Service (NGINX static serve)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: muleshield-pro-v2
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
        - name: frontend
          image: nginx:alpine
          volumeMounts:
            - name: static-content
              mountPath: /usr/share/nginx/html
          ports:
            - containerPort: 80
          readinessProbe:
            httpGet:
              path: /index.html
              port: 80
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /index.html
              port: 80
            initialDelaySeconds: 15
            periodSeconds: 20
          resources:
            limits:
              cpu: "200m"
              memory: "128Mi"
            requests:
              cpu: "100m"
              memory: "64Mi"
      volumes:
        - name: static-content
          configMap:
            name: frontend-html
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: frontend-html
  namespace: muleshield-pro-v2
binaryData: {}
# You can populate this ConfigMap with the contents of `ui/index.html`
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: muleshield-pro-v2
spec:
  selector:
    app: frontend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: LoadBalancer   # or NodePort for dev clusters
```

---

## 3. Configuration Details

| Component | Source | Typical Values (dev) |
|-----------|--------|----------------------|
| `ConfigMap` `muleshield-config` | Holds URLs for internal services and generic timeouts. | See **2.3 ConfigMap** above. |
| `Secret` `muleshield-secrets` | Stores `JWT_SECRET_KEY` and `POSTGRES_PASSWORD`. | Placeholder strings – replace via `kubectl create secret generic ...` before any deployment. |
| Environment variables | Injected via `envFrom` (ConfigMap + Secret) into each container. | Consistent with `backend/config.py`. |

All containers read the same environment variables, making the stack portable across clusters.

---

## 4. Health Checks & Probes

- **Readiness Probe** – `/health` endpoint (or `/index.html` for the frontend) ensures the pod only receives traffic after the service is fully started.
- **Liveness Probe** – Same endpoint, but with a longer initial delay; a failure triggers a restart by the kubelet.
- **Failure thresholds** – Default (`failureThreshold: 3`) are sufficient for dev; adjust for production.

---

## 5. Scaling Strategy

- Deployments use a **horizontal pod autoscaler (HPA)** based on CPU utilization (example below).
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ml-service-hpa
  namespace: muleshield-pro-v2
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-service
  minReplicas: 2
  maxReplicas: 5
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```
- Similar HPAs can be created for the API gateway, graph service, and frontend.
- Stateful services (PostgreSQL, Kafka) typically stay at a single replica in dev; for production you would use a StatefulSet with persistent volume claims and more replicas.

---

## 6. Rollback Procedure

1. **Identify the previous Deployment revision** (Kubernetes keeps a revision history for Deployments).
   ```bash
   kubectl rollout history deployment/ml-service -n muleshield-pro-v2
   ```
2. **Roll back** to a known‑good revision:
   ```bash
   kubectl rollout undo deployment/ml-service -n muleshield-pro-v2 --to-revision=2
   ```
3. Verify the rollback succeeded:
   ```bash
   kubectl get pods -l app=ml-service -n muleshield-pro-v2
   kubectl logs <pod-name> -n muleshield-pro-v2
   ```
4. Re‑apply any ConfigMap or Secret changes if they were part of the faulty release.

> **Note**: Because we are using immutable Docker images (`:latest` tags in the examples), ensure you **re‑build and push a new image** before each rollout.  Tagging images with a Git SHA (`myservice:<commit‑sha>`) makes rollbacks deterministic.

---

## 7. Next Steps & Validation

1. **Build Docker images** for each service (`docker build -t muleshield/<service>:<tag> .`).
2. **Push** them to a registry accessible by the cluster.
3. **Apply** the manifests:
   ```bash
   kubectl apply -f k8s/namespace.yaml
   kubectl apply -f k8s/secrets.yaml   # after creating real secret values
   kubectl apply -f k8s/configmap.yaml
   kubectl apply -f k8s/postgres.yaml
   kubectl apply -f k8s/kafka.yaml
   kubectl apply -f k8s/api-gateway.yaml
   kubectl apply -f k8s/ml-service.yaml
   kubectl apply -f k8s/graph-service.yaml
   kubectl apply -f k8s/reporting-service.yaml
   kubectl apply -f k8s/frontend.yaml
   ```
4. **Validate** each service via its `/health` endpoint using `curl` or `kubectl port-forward`.
5. Run a **smoke test**: call the API gateway `/api/auth/signup` → `/api/auth/login` → `/api/model-registry/retrain` and ensure the downstream services respond.

Until the above steps are executed successfully, the Kubernetes deployment should be regarded as **development‑only** and not production‑ready.

---

*Document generated automatically by Antigravity agent on 2026‑08‑26.*
