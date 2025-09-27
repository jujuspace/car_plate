# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a car plate AI project designed to identify hit-and-run suspects through license plate recognition. The project is in early development stage and requires data download from Google Drive.

## Project Structure

```
car_plate_AI/
├── data/                    # Data storage directory
│   ├── origin_video.mp4    # Input video for processing
│   ├── target/             # Output directory for processed results
│   └── sub_target/         # Secondary output directory
├── jujuspace/              # Development workspace
└── car_inform.json         # Configuration file for car information
```

## Development Guidelines

- This project aims to identify hit-and-run suspects using AI-based license plate recognition
- Data files must be downloaded from Google Drive before development
- **Each developer should create their own folder for code development**
- Additional data should be uploaded to Google Drive with shared links
- The data directory contains video files for car plate recognition processing
- No build tools, dependencies, or testing frameworks are currently configured
- No specific programming language or framework has been chosen yet

## Data Directory Structure

- `data/origin_video.mp4`: Source video file for car plate detection
- `data/target/`: Intended for processed output files
- `data/sub_target/`: Intended for secondary processing results
- `car_inform.json`: Configuration file (currently empty)

## Future Development

When implementing the car plate AI functionality, consider:
- Choosing appropriate computer vision libraries (OpenCV, YOLO, etc.)
- Setting up proper dependency management
- Implementing video processing pipeline
- Adding configuration management for `car_inform.json`