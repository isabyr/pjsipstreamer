# PJSIP with call audio capturing and streaming features
PJSIP library is modified to capture PCM frames from the call and stream PCM frames to the calls.

## Core classes
Added two classes to `media.hpp` and `media.cpp` files:
 - `AudioMediaCapture`: contains list to accumulate incoming frames, frames can be extracted with `getFrames/getFramesAsString` methods.
 - `AudioMediaStream`: contains list for outgoing frames, frames can be populated with `putFrame/putFrameAsString` methods.

## PJSUA2/SWIG
Need some changes to SWIG to access those features from the Python:
- Uncomment `USE_THREADS = -threads -DSWIG_NO_EXPORT_ITERATOR_METHODS` in `swig/python/Makefile`
- Add typemaps to `swig/pjsua2.i` to send/receive `bytes` from Python:
```
#ifdef SWIGPYTHON
  %typemap(in) (char *data, size_t datasize) {
    Py_ssize_t len;
    PyBytes_AsStringAndSize($input, &$1, &len);
    $2 = (size_t)len;
  }

  %typemap(in, numinputs=0) (char **data, size_t *datasize)(char *temp, size_t tempsize) {
    $1 = &temp;
    $2 = &tempsize;
  }

  %typemap(argout) (char **data, size_t *datasize) {
    if(*$1) {
      $result = PyBytes_FromStringAndSize(*$1, *$2);
      free(*$1);
    }
  }
#endif
```

## Run Demo
 1. `docker-compose up`
 2. `docker-compose exec pjsip python demo.py`
Demo script dumps frames to from the call to `pjsip/pjsuademo/output.lpcm` and streams `hw.raw` to the call. The recording of the call with both parties will be in `asterisk_files/recordings` directory. 
