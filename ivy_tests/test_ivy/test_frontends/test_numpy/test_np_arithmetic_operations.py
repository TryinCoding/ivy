# global
import numpy as np
from hypothesis import given, strategies as st

# local
import ivy_tests.test_ivy.helpers as helpers
import ivy.functional.backends.numpy as ivy_np


@st.composite
def _where(draw):
    _, values = draw(helpers.dtype_and_values(("bool",)))
    return draw(st.just(values) | st.just(True))


# add
@given(
    dtype_and_x=helpers.dtype_and_values(ivy_np.valid_float_dtypes, 2),
    dtype=st.sampled_from(ivy_np.valid_float_dtypes + (None,)),
    where=_where(),
    as_variable=helpers.array_bools(),
    with_out=st.booleans(),
    num_positional_args=helpers.num_positional_args(
        fn_name="ivy.functional.frontends.numpy.add"
    ),
    native_array=helpers.array_bools(),
)
def test_numpy_add(
    dtype_and_x,
    dtype,
    where,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    fw,
):
    input_dtype, x = dtype_and_x
    where_array = isinstance(where, list)
    if where_array:
        where = np.asarray(where, dtype=np.bool)
        input_dtype += ["bool"]
        as_variable += [False]
        native_array += [False]
    values = helpers.test_frontend_function(
        input_dtype,
        as_variable,
        with_out,
        num_positional_args,
        native_array,
        fw,
        "numpy",
        "add",
        x1=np.asarray(x[0], dtype=input_dtype[0]),
        x2=np.asarray(x[1], dtype=input_dtype[1]),
        out=None,
        where=where,
        casting="same_kind",
        order="k",
        dtype=dtype,
        subok=True,
        test_values=False,
    )
    if values is None:
        return
    ret, frontend_ret = values
    ret_flat = [np.where(where, x, np.zeros_like(x)) for x in helpers.flatten(ret)]
    frontend_ret_flat = [
        np.where(where, x, np.zeros_like(x)) for x in helpers.flatten(frontend_ret)
    ]
    helpers.value_test(ret_flat, frontend_ret_flat)