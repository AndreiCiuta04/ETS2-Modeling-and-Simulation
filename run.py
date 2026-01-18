def run_model(model, steps):
    """
    Runs the model for a given number of steps.
    """
    for _ in range(steps):
        model.step()
