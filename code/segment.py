import numpy as np

def slidingwindowsegment(sequence, create_segment, compute_error, max_error, seq_range=None):
    """
    Return a list of line segments that approximate the sequence.

    The list is computed using the sliding window technique. 

    Parameters
    ----------
    sequence : sequence to segment
    create_segment : a function of two arguments (sequence, sequence range) that returns a line segment that approximates the sequence data in the specified range
    compute_error: a function of two argments (sequence, segment) that returns the error from fitting the specified line segment to the sequence data
    max_error: the maximum allowable line segment fitting error

    """
    if not seq_range:
        seq_range = (0,len(sequence)-1)

    start = seq_range[0]
    end = start
    result_segment = create_segment(sequence,(seq_range[0],seq_range[1]))
    while end < seq_range[1]:
        end += 1
        test_segment = create_segment(sequence,(start,end))
        error = compute_error(sequence,test_segment)
        if error <= max_error:
            result_segment = test_segment
        else:
            break

    if end == seq_range[1]:
        return [result_segment]
    else:
        return [result_segment] + slidingwindowsegment(sequence, create_segment, compute_error, max_error, (end-1,seq_range[1]))
        
def bottomupsegment(sequence, create_segment, compute_error, max_error):
    """
    Return a list of line segments that approximate the sequence.
    
    The list is computed using the bottom-up technique.
    
    Parameters
    ----------
    sequence : sequence to segment
    create_segment : a function of two arguments (sequence, sequence range) that returns a line segment that approximates the sequence data in the specified range
    compute_error: a function of two argments (sequence, segment) that returns the error from fitting the specified line segment to the sequence data
    max_error: the maximum allowable line segment fitting error
    
    """
    segments = [create_segment(sequence,seq_range) for seq_range in zip(range(len(sequence))[:-1],range(len(sequence))[1:])]
    mergesegments = [create_segment(sequence,(seg1[0],seg2[2])) for seg1,seg2 in zip(segments[:-1],segments[1:])]
    mergecosts = [compute_error(sequence,segment) for segment in mergesegments]

    while min(mergecosts) < max_error:
        idx = mergecosts.index(min(mergecosts))

        new_seg = create_segment(sequence, (segments[idx][0], segments[idx + 1][2]))
        segments[idx] = new_seg
        del segments[idx + 1]

        if idx > 0:
            merge_seg = create_segment(sequence, (segments[idx - 1][0], segments[idx][2]))
            mergecosts[idx - 1] = compute_error(sequence, merge_seg)

        if idx + 1 < len(mergecosts):
            merge_seg = create_segment(sequence, (segments[idx][0], segments[idx + 1][2]))
            mergecosts[idx] = compute_error(sequence, merge_seg)

        del mergecosts[idx]

    return segments
    
def topdownsegment(sequence, create_segment, compute_error, max_error, seq_range=None):
    """
    Return a list of line segments that approximate the sequence.
    
    The list is computed using the bottom-up technique.
    
    Parameters
    ----------
    sequence : sequence to segment
    create_segment : a function of two arguments (sequence, sequence range) that returns a line segment that approximates the sequence data in the specified range
    compute_error: a function of two argments (sequence, segment) that returns the error from fitting the specified line segment to the sequence data
    max_error: the maximum allowable line segment fitting error
    
    """
    if not seq_range:
        seq_range = (0,len(sequence)-1)

    bestlefterror,bestleftsegment = float('inf'), None
    bestrighterror,bestrightsegment = float('inf'), None
    bestidx = None

    for idx in range(seq_range[0]+1,seq_range[1]):
        segment_left = create_segment(sequence,(seq_range[0],idx))
        error_left = compute_error(sequence,segment_left)
        segment_right = create_segment(sequence,(idx,seq_range[1]))
        error_right = compute_error(sequence, segment_right)
        if error_left + error_right < bestlefterror + bestrighterror:
            bestlefterror, bestrighterror = error_left, error_right
            bestleftsegment, bestrightsegment = segment_left, segment_right
            bestidx = idx
    
    if bestlefterror <= max_error:
        leftsegs = [bestleftsegment]
    else:
        leftsegs = topdownsegment(sequence, create_segment, compute_error, max_error, (seq_range[0],bestidx))
    
    if bestrighterror <= max_error:
        rightsegs = [bestrightsegment]
    else:
        rightsegs = topdownsegment(sequence, create_segment, compute_error, max_error, (bestidx,seq_range[1]))
    
    return leftsegs + rightsegs


def m_swab(sequence, create_segment, compute_error, max_error, buffer_size=80):
    """
        Described in Van Laerhoven, Kristof, and Bernt Schiele.
        "An Empirical Study of Time Series Approximation Algorithms for Wearable Accelerometers." (2009).

        Return a list of line segments that approximate the sequence.

        The list is computed using the bottom-up technique.

        Parameters
        ----------
        sequence : sequence to segment
        create_segment : a function of two arguments (sequence, sequence range) that returns a line segment that approximates the sequence data in the specified range
        compute_error: a function of two argments (sequence, segment) that returns the error from fitting the specified line segment to the sequence data
        max_error: the maximum allowable line segment fitting error

    """

    segs = []
    win_left = 0
    win_right = buffer_size-1

    seq_range = (0, len(sequence)-1)

    while True:  #while new data:
        swabbuf = sequence[win_left:win_right]
        # Bottom-Up segmentation of buffer
        T = bottomupsegment(swabbuf, create_segment, compute_error, max_error)

        # add left-most segment from BU:
        segs.append(T[0])
        n = len(segs)

        # merge last segments if slope is equal
        if n > 2:
            last_slope = (segs[-1][3] - segs[-1][1]) // (segs[-1][2] - segs[-1][0])
            b_last_slope = (segs[-2][3] - segs[-2][1]) // (segs[-2][2] - segs[-2][0])
            if last_slope == b_last_slope:
                # merge segments
                new_segs = segs[:-2]
                merged = create_segment(sequence, (segs[-2][0], segs[-1][2]))
                new_segs.append(merged)
                segs = new_segs
                n -= 1

        # shift left of buffer window:
        win_left += segs[-1][0]
        # shift right of buffer window:
        if win_right < seq_range[1]:
            i = win_right + 1
            # get sign of the slope
            s = np.sign(sequence[i] - sequence[i-1])
            while np.sign(sequence[i] - sequence[i-1]) == s:
                i += 1
                if i >= seq_range[1]:
                    i -= 1
                    break
            win_right = i
        else:
            # all done, flush buffer segments:
            segs += T[1:]
            return segs