#!/bin/bash

# Define the models to benchmark
MODELS=("qwen3:8b" "qwen3:4b" "gemma3:4b")

# Base directories
BACKEND_DIR="../backend"
BENCHMARK_DIR="."

echo "Starting automated benchmarks..."

# Activate virtual environment
source ${BACKEND_DIR}/venv/bin/activate

for model in "${MODELS[@]}"; do
    echo "========================================================="
    echo "Benchmarking Model: $model"
    echo "========================================================="

    # 1. Update the .env file with the current model
    echo "Updating CHAT_MODEL in .env to $model..."
    sed -i "s/^CHAT_MODEL=.*/CHAT_MODEL=${model}/" ${BACKEND_DIR}/.env

    # 2. Start the FastAPI backend in the background
    echo "Starting FastAPI backend..."
    cd ${BACKEND_DIR}
    uvicorn app.main:app --port 8000 &
    UVICORN_PID=$!
    
    # Return to benchmarks dir silently
    cd - > /dev/null

    # Wait for the backend to be fully ready
    echo "Waiting for backend to initialize (10 seconds)..."
    sleep 10

    # 3. Run the Locust tests for different scenarios
    SAFE_MODEL_NAME=$(echo $model | tr ':' '-')
    
    # Define scenarios: "users spawn_rate duration"
    SCENARIOS=(
        "1 1 2m"
        "5 1 2m"
        "10 2 3m"
        "20 2 5m"
    )

    for scenario in "${SCENARIOS[@]}"; do
        read -r users rate duration <<< "$scenario"
        echo "Running Locust test: ${users} users, ${rate}/sec spawn rate, for ${duration}..."
        locust -f locustfile.py \
               --headless \
               -u $users \
               -r $rate \
               -t $duration \
               --host=http://localhost:8000 \
               --csv=results_${SAFE_MODEL_NAME}_${users}users
               
        echo "Finished scenario with ${users} users."
        echo "Waiting 5 seconds before next scenario..."
        sleep 5
    done

    # 4. Stop the FastAPI backend
    echo "Stopping FastAPI backend (PID: $UVICORN_PID)..."
    kill $UVICORN_PID
    wait $UVICORN_PID 2>/dev/null

    # Give Ollama a moment to unload the model before starting the next one
    sleep 5

    echo "Finished benchmarking $model!"
    echo ""
done

echo "All benchmarks complete!"
echo "Compiling the final report card..."
python3 generate_report.py
