Track reconstruction made easy
==============================

This is a pet project to do track reconstruction,
based on real data coming from the LHCb detector at CERN.

Think you can make it better? Go ahead and try!

>    python3 simple_track_forwarding.py

What is track reconstruction?
-----------------------------

At the LHCb detector, millions of particles collide at speeds
close to the speed of light, leaving traces (hits) on the modules
placed in their way.

The collisions that happen at the same time are packed
into an *event*, and sent to one of our servers,
that must reconstruct the tracks that formed each particle
in real time.

This project contains events in json format. These events are
then processed by some reconstruction algorithm, and finally
the results are validated. That is, the particles found by
the solver are matched against the real particles that came out of
the collisions in the event.

![velopix reconstruction example](doc/reco_example.png "velopix reconstruction example")

The algorithm included is just one way of doing it, but perhaps
not the most efficient one!

Diving into details
-------------------

Input files are specified in json. An *event model* to parse them
is shipped with this project.

    $ python3
    Python 3.4.3 (default, Mar 31 2016, 20:42:37) 
    [GCC 5.3.1 20151207 (Red Hat 5.3.1-2)] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    > import event_model as em
    > import json
    > f = open("velojson/0.json")
    > json_data = json.loads(f.read())
    > event = em.event(json_data)
    > f.close()

The LHCb Velopix detector has 52 modules. Spread across the modules,
we should have many hits, depending on the event we are on.

    > print(len(event.modules))
    52
    > print(len(event.hits))
    1003

Hits are composed of an ID, and {x, y, z} coordinates.

    > print(event.hits[0])
    #117979 {-3.385275, 13.436796, -275.531006}

modules are placed at some z in the detector. Each module
may have as many hits as particles crossed by it, plus some noise to
make things interesting.

    > print(event.modules[0])
    module 0:
     At z: -275
     Number of hits: 18
     Hits (#id {x, y, z}): [#117979 {-3.385275, 13.436796, -275.531006}, #128942 {0.017677, 13.495132, -275.531006}, #134072 {0.464924, 12.270069, -275.531006}, #134107 {-0.896257, 10.908888, -275.531006}, #134562 {1.417747, 13.067333, -275.531006}, #141439 {3.828983, 13.37846, -275.531006}, #178943 {4.529018, 2.722359, -275.531006}, #193779 {7.231934, 0.913937, -275.531006}, #268042 {24.997992, 21.066479, -274.468994}, #326966 {14.341893, 28.261292, -274.468994}, #389073 {-1.207973, 31.742023, -274.468994}, #542432 {3.986314, -5.6763, -274.468994}, #557605 {13.572914, -10.634886, -274.468994}, #569059 {7.894847, -1.534422, -274.468994}, #573093 {10.928335, -3.323402, -274.468994}, #861641 {30.529337, -0.678823, -275.531006}, #905103 {26.154114, -9.526497, -275.531006}, #941420 {21.934456, -16.507406, -275.531006}]

A simplistic implementation runs through all modules sequentially,
finding tracks by matching hits in a straight line.

    > from classical_solver import classical_solver
    > tracks = classical_solver().solve(event)
    > len(tracks)
    117
    > print(tracks[0])
    Track hits #14: [#53557115 {5.485382, -22.965059, 736.968994}, #51465608 {5.115919, -21.623325, 686.968994}, #49373845 {4.785345, -20.28159, 636.968994}, #47282337 {4.435328, -18.959301, 586.968994}, #45196219 {3.754736, -16.295275, 486.968994}, #43110101 {3.093594, -13.611805, 386.968994}, #41020905 {2.646347, -11.608925, 311.968994}, #38928886 {2.315776, -10.267189, 261.968994}, #36834557 {2.160213, -9.567154, 236.968994}, #34078922 {2.100107, -9.273705, 225.531006}, #31983573 {1.944543, -8.573669, 200.531006}, #29887968 {1.769534, -7.89308, 175.531006}, #27792619 {1.613971, -7.193043, 150.531006}, #25697270 {1.438962, -6.512453, 125.530998}]

Finally, we should validate these results, and we'll look
at three things:

*   Reconstruction Efficiency: The fraction of real particles we have reconstructed.
    > \# correctly reconstructed / \# real tracks

*   Clone Tracks: Tracks that are similar to other correctly reconstructed tracks.
    > \# clone tracks / \# correctly reconstructed

*   Ghost Tracks: Tracks that are incorrect, either created by noise or by incorrectly reconstructing a track.
    > \# incorrectly reconstructed / \# all reconstructed

We will get the validation detailed for different kinds of particles.

    > import validator_lite as vl
    > vl.validate_print([json_data], [tracks])
    117 tracks including        3 ghosts (  2.6%). Event average   2.6%
                  velo :      107 from      114 ( 93.9%,  93.9%)        2 clones (  1.87%), purity: ( 98.99%,  98.99%),  hitEff: ( 98.01%,  98.01%)
                  long :       39 from       39 (100.0%, 100.0%)        2 clones (  5.13%), purity: ( 97.98%,  97.98%),  hitEff: ( 96.74%,  96.74%)
             long5GeV :       30 from       30 (100.0%, 100.0%)        2 clones (  6.67%), purity: ( 98.03%,  98.03%),  hitEff: ( 96.45%,  96.45%)
          long_strange :        2 from        2 (100.0%, 100.0%)        0 clones (  0.00%), purity: (100.00%, 100.00%),  hitEff: (100.00%, 100.00%)
    None
            long_fromb :       13 from       13 (100.0%, 100.0%)        0 clones (  0.00%), purity: ( 98.46%,  98.46%),  hitEff: ( 98.46%,  98.46%)
       long_fromb5GeV :       12 from       12 (100.0%, 100.0%)        0 clones (  0.00%), purity: (100.00%, 100.00%),  hitEff: (100.00%, 100.00%)
