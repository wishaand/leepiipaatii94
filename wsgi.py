import sys
import traceback

print("=" * 50, file=sys.stderr)
print("🚀 wsgi.py is loading...", file=sys.stderr)

try:
    from app import create_app
    print("✅ Successfully imported create_app", file=sys.stderr)
    
    app = create_app()
    print("✅ Flask app created successfully", file=sys.stderr)
    
except Exception as e:
    print(f"❌ FATAL ERROR: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

print("=" * 50, file=sys.stderr)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5001)
