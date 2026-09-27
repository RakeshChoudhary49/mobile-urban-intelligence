import argparse
import config
import os
from pipeline import Pipeline

def main():
    parser = argparse.ArgumentParser(description="Edge AI Video Processing Pipeline")
    parser.add_argument("--video", type=str, required=True, help="Path to input video file")
    parser.add_argument("--bus-code", type=str, help="Bus identifier code", default="BUS-101")
    parser.add_argument("--api-url", type=str, help="Backend API URL", default=config.API_URL)
    parser.add_argument("--show", action="store_true", help="Display annotated frames")
    parser.add_argument("--save-output", action="store_true", help="Save annotated video output")
    
    args = parser.parse_args()

    # Update config overrides
    config.BUS_CODE = args.bus_code
    config.API_URL = args.api_url

    if not os.path.exists(args.video):
        print(f"Error: Video file not found at {args.video}")
        return

    print("========================================")
    print("🚀 Starting Urban Intelligence Pipeline")
    print(f"🚌 Bus Code: {config.BUS_CODE}")
    print(f"📡 API URL: {config.API_URL}")
    print(f"📹 Input Video: {args.video}")
    print("========================================\n")

    pipeline = Pipeline()
    pipeline.run(args.video, show_output=args.show, save_output=args.save_output)
    
    print("\n✅ Pipeline processing completed.")

if __name__ == "__main__":
    main()
