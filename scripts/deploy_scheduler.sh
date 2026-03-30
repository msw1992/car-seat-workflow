[Unit]
Description=Seat Push Workflow Scheduler Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/workspace/projects
Environment="WORKFLOW_API_URL=http://localhost:5000/run"
Environment="SCHEDULE_HOUR=8"
Environment="SCHEDULE_MINUTE=30"
ExecStart=/usr/bin/python3 /workspace/projects/src/scheduler/scheduler_service.py
Restart=always
RestartSec=10
StandardOutput=append:/tmp/seat_push_scheduler.log
StandardError=append:/tmp/seat_push_scheduler_error.log

[Install]
WantedBy=multi-user.target
