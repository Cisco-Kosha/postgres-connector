apiVersion: v1
kind: Service
metadata:
  name:  {{ .Values.appName }}
  labels:
    app:  {{ .Values.appName }}
spec:
  ports:
  - port: {{ .Values.service.port }}
    name: http
  selector:
    app:  {{ .Values.appName }}
