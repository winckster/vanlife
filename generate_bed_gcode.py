import argparse
import math

FAR_ABOVE = 50
LENGTH_PADDING = 5
DEFAULT_SPEED = 3000


def _write(write_fn, width, x_stop, y_step, z_step, num_steps, newline=False):
    if newline:
        def _format(x, y, z, f=DEFAULT_SPEED):
            return f'G1 X{x} Y{y} Z{z} F{f}\n'
    else:
        def _format(x, y, z, f=DEFAULT_SPEED):
            return f'G1 X{x} Y{y} Z{z} F{f}'
    
    write_fn(_format(0, width, FAR_ABOVE, 300))
    write_fn(_format(0, width, 0, 300))
    write_fn(_format(x_stop, width, 0))

    right_steps = range(1, num_steps + 1, 2)
    left_steps = range(2, num_steps + 1, 2)
    for right, left in zip(right_steps, left_steps):
        write_fn(_format(x_stop, width - right * y_step, -right * z_step))
        write_fn(_format(0, width - right * y_step, -right * z_step))
        write_fn(_format(0, width - left * y_step, -left * z_step))
        write_fn(_format(x_stop, width - left * y_step, -left * z_step))
    write_fn(_format(x_stop, width - left * y_step, FAR_ABOVE))

def main(length, width, depth, max_step=1, path=None, radius=0):
    x_stop = length + LENGTH_PADDING
    width -= radius

    # Determine step size based on whether angle is < or > 45 degrees.
    if depth <= width:
        y_step = max_step
        z_step = max_step * depth / width
        num_steps = int(width / max_step)
    else:
        y_step = max_step * width / depth
        z_step = max_step
        num_steps = int(depth / max_step)

    if path is None:
        _write(print, width, x_stop, y_step, z_step, num_steps)
    else:
        with open(path, 'w') as writer:
            _write(writer.write, width, x_stop, y_step, z_step, num_steps,
                   newline=True)


if __name__ == '__main__':
    art = """
                                 ^
                                 |z
         ________________    <-y- ⨂ length (x)
        |                |
        |                 \\       |
        |                  \\      |
        |                   \\   depth
        |                    \\    |
        |                     \\   |
        |_______________________|

                          -width-

        """

    parser = argparse.ArgumentParser(
        description=art,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('length', help='The length of the lip in mm.',
                        type=float)
    parser.add_argument('width', help='The width of the lip in mm.',
                        type=float)
    parser.add_argument('depth', help='The depth of the lip in mm.',
                        type=float)
    parser.add_argument('--path', help='Path to output file. If none '
                                       'provided, will print to stdout.')
    parser.add_argument('--max_step',
                        help='The max step size in mm of movements in the y- '
                             'or z-direction. For angles of less then 45 '
                             'degrees, this will be the step size in y and the '
                             'z step size will be smaller. '
                             'For angles greater than 45 degrees, z will use '
                             'the max step size and the y step size will be '
                             'smaller.',
                        default=1,
                        type=float)
    parser.add_argument('--radius',
                        help='The radius of the cutter. This is used to '
                            'compensate for its size in the position of the '
                            'cuts',
                        default=0,
                        type=float)

    args = parser.parse_args()

    main(args.length, args.width, args.depth, path=args.path,
         max_step=args.max_step, radius=args.radius)
