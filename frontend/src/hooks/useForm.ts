import { useState, useCallback } from 'react';

interface UseFormOptions<T> {
  initialValues: T;
  onSubmit: (values: T) => void | Promise<void>;
  validate?: (values: T) => Partial<Record<keyof T, string>>;
  validateOnChange?: boolean;
  validateOnBlur?: boolean;
}

interface FormState<T> {
  values: T;
  errors: Partial<Record<keyof T, string>>;
  touched: Partial<Record<keyof T, boolean>>;
  isSubmitting: boolean;
  isValid: boolean;
}

export function useForm<T extends Record<string, any>>({
  initialValues,
  onSubmit,
  validate,
  validateOnChange = false,
  validateOnBlur = true
}: UseFormOptions<T>) {
  const [state, setState] = useState<FormState<T>>({
    values: initialValues,
    errors: {},
    touched: {},
    isSubmitting: false,
    isValid: true
  });

  const validateForm = useCallback((values: T) => {
    if (!validate) return {};
    const errors = validate(values);
    setState(prev => ({
      ...prev,
      errors,
      isValid: Object.keys(errors).length === 0
    }));
    return errors;
  }, [validate]);

  const handleChange = useCallback((
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;
    const newValues = {
      ...state.values,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    };

    setState(prev => ({
      ...prev,
      values: newValues,
      touched: {
        ...prev.touched,
        [name]: true
      }
    }));

    // Clear error when field is modified
    if (state.errors[name as keyof T]) {
      setState(prev => ({
        ...prev,
        errors: {
          ...prev.errors,
          [name]: undefined
        }
      }));
    }

    // Validate on change if enabled
    if (validateOnChange) {
      validateForm(newValues);
    }
  }, [state.values, state.errors, validateForm, validateOnChange]);

  const handleBlur = useCallback((
    e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name } = e.target;
    setState(prev => ({
      ...prev,
      touched: {
        ...prev.touched,
        [name]: true
      }
    }));

    // Validate on blur if enabled
    if (validateOnBlur && validate) {
      validateForm(state.values);
    }
  }, [state.values, validateForm, validateOnBlur, validate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Mark all fields as touched
    const touched = Object.keys(state.values).reduce((acc, key) => ({
      ...acc,
      [key]: true
    }), {} as Record<keyof T, boolean>);

    setState(prev => ({ ...prev, touched }));

    // Validate form
    if (validate) {
      const errors = validateForm(state.values);
      if (Object.keys(errors).length > 0) {
        return;
      }
    }

    setState(prev => ({ ...prev, isSubmitting: true }));
    try {
      await onSubmit(state.values);
    } catch (error) {
      console.error('Form submission error:', error);
      // Handle submission error
      setState(prev => ({
        ...prev,
        errors: {
          ...prev.errors,
          submit: error instanceof Error ? error.message : 'Form submission failed'
        }
      }));
    } finally {
      setState(prev => ({ ...prev, isSubmitting: false }));
    }
  };

  const reset = useCallback(() => {
    setState({
      values: initialValues,
      errors: {},
      touched: {},
      isSubmitting: false,
      isValid: true
    });
  }, [initialValues]);

  const setValue = useCallback((name: keyof T, value: any) => {
    setState(prev => ({
      ...prev,
      values: {
        ...prev.values,
        [name]: value
      },
      touched: {
        ...prev.touched,
        [name]: true
      }
    }));
  }, []);

  const setError = useCallback((name: keyof T, error: string) => {
    setState(prev => ({
      ...prev,
      errors: {
        ...prev.errors,
        [name]: error
      }
    }));
  }, []);

  return {
    ...state,
    handleChange,
    handleBlur,
    handleSubmit,
    reset,
    setValue,
    setError,
    validate: validateForm
  };
} 