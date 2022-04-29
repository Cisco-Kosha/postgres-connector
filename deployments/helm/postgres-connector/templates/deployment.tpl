apiVersion: apps/v1
kind: Deployment
metadata:
  name:  {{ .Values.appName }}
  labels:
    version: {{ .Values.appVersion }}
  annotations:
  name:  {{ .Values.appName }}
  labels:
    version: {{ .Values.appVersion }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app:  {{ .Values.appName }}
      version: {{ .Values.appVersion }}
  template:
    metadata:
      labels:
        app:  {{ .Values.appName }}
        version: {{ .Values.appVersion }}
    spec:
      containers:
      - name: {{ .Values.appName }}
        image: docker.io/{{ .Values.image.repository }}/{{ .Values.image.name }}:{{ .Values.image.tag }}
        resources:
          requests:
            cpu: "100m"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - containerPort: {{ .Values.service.port }}
        env:
        - name: DATABASE
          value: {{ .Values.connector.database }}
        - name: DB_USER
          value: {{ .Values.connector.db_user }}
        - name: DB_PASSWORD
          value: {{ .Values.connector.db_password }}
        - name: DB_SERVER
          value: {{ .Values.connector.db_host }}
        - name: DB_NAME
          value: {{ .Values.connector.db_name }}
        {{ if .Values.connector.db_port -}}
        - name: DB_PORT
          value: "{{ .Values.connector.db_port }}"
        {{ end -}}
