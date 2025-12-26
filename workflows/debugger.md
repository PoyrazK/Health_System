---
description: Debugger Agent - Error diagnosis, memory optimization, and performance tuning
---

# Debugger Agent 🐛

Your role is to diagnose errors, fix bugs, and optimize performance.

## Core Responsibilities
1. Error diagnosis and fixing
2. Memory optimization
3. Performance profiling
4. Code quality checks

## Workflow

### Step 1: Common ML Errors

**Memory Errors:**
```python
# Reduce memory usage
def reduce_memory(df):
    for col in df.columns:
        if df[col].dtype == 'float64':
            df[col] = df[col].astype('float32')
        if df[col].dtype == 'int64':
            df[col] = df[col].astype('int32')
    return df
```

**NaN/Inf Errors:**
```python
# Check for problematic values
def check_data_quality(df):
    print("NaN counts:", df.isna().sum().sum())
    print("Inf counts:", np.isinf(df.select_dtypes(np.number)).sum().sum())
```

### Step 2: Profiling

```python
import cProfile
import pstats

def profile_function(func, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats(20)
    return result
```

### Step 3: Memory Profiling

```python
from memory_profiler import profile

@profile
def memory_heavy_function():
    # Your code here
    pass
```

### Step 4: Common Fixes

**Slow Training:**
- Reduce data size for quick iterations
- Use `n_jobs=-1` for parallelization
- Enable early stopping
- Sample data for hyperparameter search

**Out of Memory:**
- Process data in chunks
- Use float32 instead of float64
- Clear unused variables with `del` and `gc.collect()`
- Use generators for large datasets

**Overfitting:**
- Add regularization
- Reduce model complexity
- Add more data augmentation
- Use cross-validation

### Step 5: Quick Debug Commands
// turbo
```bash
# Check Python memory
python -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"
```

## Output Artifacts
- Bug fix commits
- Performance reports
- Memory optimization changes
