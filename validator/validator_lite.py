from event_model.event_model import track, hit
import argparse
import errno
import os
import numpy as np
import itertools


class validator_event(object):
    """A SOA datastructure for events"""
    def __init__(self, module_prefix_sum, hit_Xs, hit_Ys, hit_Zs, hits, mcp_to_hits=None):
        self.module_prefix_sum = module_prefix_sum
        self.hit_Xs, self.hit_Ys, self.hit_Zs = hit_Xs, hit_Ys, hit_Zs
        self.hits = hits
        self.mcp_to_hits = mcp_to_hits
        self.hit_to_mcp = None
        self.particles = None
        if self.mcp_to_hits is not None:
            self.particles = list(self.mcp_to_hits.keys())
            self.hit_to_mcp = {h:[] for h in self.hits}
            for mcp,mhits in iter(mcp_to_hits.items()):
                for h in mhits:
                    self.hit_to_mcp[h].append(mcp)

    def get_hit(self, hit_id):
        return self.hits[hit_id]


class MCParticle(object):
    """Store information about a Monte-Carlo simulation particle"""

    def __init__(self, pkey, pid, p, pt, eta, phi, charge, velohits):
        """Construct a new particle from

        its numeric key (arbitrary integer used in input file)
        its pID (integer providing information on the particle type)
        its p, pt, eta and phi parameters
        its assocated velopixel hits"""
        self.pkey = pkey
        self.pid = pid
        self.velohits = velohits
        self.p = p
        self.pt = pt
        self.eta = eta
        self.phi = phi
        self.charge = charge

        # flags - set them directly after initializing the object
        self.islong = False
        self.isdown = False
        self.isvelo = False
        self.isut = False
        self.hasScifi = False
        self.strange = False
        self.fromb = False
        self.fromcharm = False
        self.over5 = abs(self.p) > 5000.

    def __str__(self):
        s = "MCParticle %d:\n"%self.pkey
        s += "\tpid:\t%d"%(self.pid)
        s += "\tp:\t%g"%(self.p)
        s += "\tp:\t%g"%(self.pt)
        s += "\teta:\t%g"%(self.eta)
        s += "\tphi:\t%g\n"%(self.phi)
        s += "\tislong:\t%r"%(self.islong)
        s += "\tisdown:\t%r"%(self.isdown)
        s += "\tisvelo:\t%r"%(self.isvelo)
        s += "\tisut:\t%r\n"%(self.isut)
        s += "\tfromstrange:\t%r"%(self.strange)
        s += "\tfromb:\t%r"%(self.fromb)
        s += "\tfromcharm:\t%r"%(self.fromcharm)
        s += "\nhits:"+str(self.velohits)
        return s

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)


def parse_json_data(json_data):
    hits = []
    for hid, (x, y, z) in enumerate(zip(json_data["x"], json_data["y"], json_data["z"])):
        hits.append(hit(x, y, z, hid))
    mcp_to_hits = {}
    if json_data["montecarlo"]:
        description = json_data["montecarlo"]["description"]
        particles = json_data["montecarlo"]["particles"]
        for p in particles:
            d = {description[i]: p[i] for i in range(len(description))}
            trackhits = [hits[hit_number] for hit_number in d["hits"]]
            mcp = MCParticle(d.get("key", 0), d.get("pid", 0), d.get("p", 0), d.get("pt", 0), d.get("eta", 0), d.get("phi", 0), d.get("charge", 0), trackhits)
            mcp.islong, mcp.isdown, mcp.isvelo, mcp.isut, mcp.hasScifi = d.get("isLong", 0), d.get("isDown", 0), d.get("hasVelo", 1), d.get("hasUT", 0), d.get("hasScifi", 0)
            mcp.strange, mcp.fromb, mcp.fromcharm = d.get("fromStrangeDecay", 0), d.get("fromBeautyDecay", 0), d.get("fromCharmDecay", 0)
            mcp_to_hits[mcp] = trackhits
    return validator_event (json_data["module_prefix_sum"], json_data["x"], json_data["y"], json_data["z"], hits, mcp_to_hits)

class Efficiency(object):

    def __init__(self, t2p, p2t, particles, event, label):
        self.label = label
        self.n_particles = 0
        self.n_reco = 0
        self.n_pure = 0
        self.n_clones = 0
        self.n_events = 0
        self.n_heff = 0
        self.n_hits = 0
        self.recoeff = []
        self.purity = []
        self.hiteff = []
        self.recoeffT= 0.0
        self.purityT = 0.0
        self.hiteffT = 0.0
        self.avg_recoeff = 0.0
        self.avg_purity = 0.0
        self.avg_hiteff = 0.0
        self.add_event(t2p, p2t, particles, event)

    def add_event(self, t2p, p2t, particles, event):
        self.n_events += 1
        self.n_particles += len(particles)
        self.n_reco += len(reconstructed(p2t))
        self.recoeff.append(1.*self.n_reco/self.n_particles)
        self.n_clones += sum([len(t)-1 for t in list(clones(t2p).values())])
        hit_eff = hit_efficinecy(t2p, event.hit_to_mcp, event.mcp_to_hits)
        purities = [pp[0] for _, pp in iter(t2p.items()) if pp[1] is not None]
        self.n_pure +=np.sum(purities)
        self.n_heff +=np.sum(list(hit_eff.values()))
        self.n_hits +=len(hit_eff)
        if len(hit_eff) > 0: self.hiteff.append(np.mean(list(hit_eff.values())))
        if len(purities) > 0: self.purity.append(np.mean(purities))
        if len(self.recoeff) > 0: self.avg_recoeff = 100.*np.mean(self.recoeff)
        if len(self.purity) > 0: self.avg_purity = 100.*np.mean(self.purity)
        if len(self.hiteff) > 0: self.avg_hiteff = 100.*np.mean(self.hiteff)
        if self.n_particles > 0:
            self.recoeffT = 100. * self.n_reco / self.n_particles
        if self.n_reco > 0:
            self.purityT = 100. * self.n_pure / (self.n_reco + self.n_clones)

    def __str__(self):
        clone_percentage = 0
        if self.n_reco > 0: clone_percentage = 100.*self.n_clones/self.n_reco

        hit_eff = 0
        if self.n_hits > 0: hit_eff = 100.*self.n_heff/self.n_hits

        s = "%18s : %8d from %8d (%5.1f%%, %5.1f%%) %8d clones (%6.2f%%), purity: (%6.2f%%, %6.2f%%),  hitEff: (%6.2f%%, %6.2f%%)"%(self.label
            , self.n_reco, self.n_particles, self.recoeffT, self.avg_recoeff
            , self.n_clones, clone_percentage, self.purityT
            , self.avg_purity,self.avg_hiteff, hit_eff)
        return s

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

def update_efficiencies(eff, event, tracks, weights, label, cond):
    #t2p_filtered = {t:(w,p) for t,(w,p) in t2p.iteritems() if (p is None) or cond(p)}
    particles_filtered = {p for p in event.particles if cond(p)}
    pidx_filtered = [-1]
    if len(particles_filtered) > 0:
        pidx_filtered, particles_filtered = zip(*[(ip,p) for ip, p in enumerate(event.particles) if cond(p)])
    else:
        return eff
    weights_filtered = weights[:,np.array(list(pidx_filtered))]
    t2p,p2t = hit_purity(tracks, particles_filtered, weights_filtered)
    if eff is None:
        eff = Efficiency(t2p, p2t, particles_filtered, event, label)
    else:
        eff.add_event(t2p, p2t, particles_filtered, event)

    return eff

def comp_weights(tracks, event):
    """
    Compute w(t,p)
    The fraction of hits a particle p contributes to all hits of a track t.

    Keyword arguments:
    tracks -- a list of reconstructed tracks
    event -- an insance of event_model.Event holding all information related to this event.
    """
    w = np.zeros((len(tracks), len(event.particles)))
    for i, j in itertools.product(range(len(tracks)), range(len(event.particles))):
        trackhits = tracks[i].hits
        nhits = len(trackhits)
        if nhits >= 2:
            particle = event.particles[j]
            # try:
            nhits_from_p = len([h for h in trackhits if event.hit_to_mcp[h].count(particle) > 0])
            # except:
            #     print(event.hit_to_mcp)
            #     raise
            w[i,j] = float(nhits_from_p)/nhits
    return w

def hit_purity(tracks, particles, weights):
    """
    Construct purity and reconstruction tables
    This function generates two dicts. The first stores the purities for all
    tracks. A track that has no particle associated (max(w(t,p)) <= 0.7) still
    stores the max particle weight but has no particle associated.
    The second table stores for each particle track for which this particle header
    the maximum weight. If none of its weights were > 0.7 it said to be not
    reconstructed.

    Keyword arguments:
    tracks -- a list of reconstructed tracks
    particles -- a list of Monte-Carlo particles
    weights -- the w(t,p) table calculated with comp_weights
    """
    # initialize hit purities for tracks t.
    t2p = {t:(0.0, None) for t in tracks}
    # initialize reconstruction table for particles p.
    p2t = {p:(0.0, None) for p in particles}
    for i in range(len(tracks)):
        # for each track get all particle weights and detmine max
        wtp, nwtp = np.max(weights[i,:]), np.argmax(weights[i,:])
        if wtp > 0.7:
            t2p[tracks[i]] = (wtp, particles[nwtp])
        else:
            # store the weight anyway but don't associate a particle since this
            # track has no particle associated (i.e. it is a ghost)
            t2p[tracks[i]] = (wtp, None)
    for i in range(len(particles)):
        wtp, nwtp = np.max(weights[:,i]), np.argmax(weights[:,i])
        if wtp > 0.7:
            p2t[particles[i]] = (wtp, tracks[nwtp])
        else:
            p2t[particles[i]] = (wtp, None)
    return t2p, p2t

def hit_efficinecy(t2p, hit_to_mcp, mcp_to_hits):
    """
    Hit efficiency for associated tracks.
    Calculate the hit efficiency for pairs of tracks and their associated
    particle (if any exists).

    Keyword arguments:
    t2p -- hit purity table as caclulated by hit_purity()
    hit_to_mcp -- hit to MC particles dictionary from event data structure
    mcp_to_hits -- MC particle to hits dictionary from event data structure
    """
    hit_eff = {}
    for track, (_, particle) in iter(t2p.items()):
        if particle is None:
            continue
        # for each track that is associated to a particle

        # number of hits from particle on track
        hits_p_on_t = sum([hit_to_mcp[h].count(particle) for h in track.hits])
        # # hits from p on t / total # hits from p
        hit_eff[(track, particle)] = float(hits_p_on_t)/len(mcp_to_hits[particle])
    return hit_eff


def reconstructed(p2t):
    "Returns all reconstructed tracks"
    return [t for _,(_,t) in  iter(p2t.items()) if t is not None]


def clones(t2p):
    "Returns dictionary of particles that have clones (multiple track assocs)"
    p2t = {}
    for track, (_, particle) in iter(t2p.items()):
        if particle is not None:
            # for each associated track
            if particle not in p2t:
                # if this is the first time we see this particle, initialize
                p2t[particle] = []
            # add this track to the list of tracks associated with this particle
            p2t[particle].append(track)
    # if more than one track is associated with a particle, it is a clone.
    return {p:t for p,t in iter(p2t.items()) if len(t) > 1}

def ghosts(t2p):
    "Return ghosts, i.e. list of tracks with no particle associated"
    return [t for t,pp in iter(t2p.items()) if pp[1] is None]

def ghost_rate(t2p):
    "Returns the fraction of unassociated tracks (fake tracks) and number of ghosts"
    ntracks = len(t2p.keys())
    nghosts = len(ghosts(t2p))
    return float(nghosts)/ntracks, nghosts

def validate_print(events_json_data, tracks_list):
    tracking_data = []
    for event, tracks in zip(events_json_data, tracks_list):
        tracking_data.append((parse_json_data(event), tracks))

    n_tracks = 0
    avg_ghost_rate = 0.0
    n_allghsots = 0
    eff_velo = None
    eff_long = None
    eff_long5 = None
    eff_long_strange = None
    eff_long_strange5 = None
    eff_long_fromb = None
    eff_long_fromb5 = None
    for event, tracks in tracking_data:
        n_tracks += len(tracks)
        weights = comp_weights(tracks, event)
        t2p, _ = hit_purity(tracks, event.particles, weights)
        grate, nghosts = ghost_rate(t2p)
        n_allghsots += nghosts
        avg_ghost_rate += grate
        eff_velo = update_efficiencies(eff_velo, event, tracks, weights, 'velo'
                    , lambda p: p.isvelo and (abs(p.pid) != 11))
        eff_long = update_efficiencies(eff_long, event, tracks, weights, 'long'
                    , lambda p: p.islong and (abs(p.pid) != 11))
        eff_long5 = update_efficiencies(eff_long5, event, tracks, weights, 'long>5GeV'
                    , lambda p: p.islong and p.over5 and (abs(p.pid) != 11))
        eff_long_strange = update_efficiencies(eff_long_strange, event, tracks, weights, 'long_strange'
                    , lambda p: p.islong and p.strange and (abs(p.pid) != 11))
        eff_long_strange5 = update_efficiencies(eff_long_strange5, event, tracks, weights, 'long_strange>5GeV'
                    , lambda p: p.islong and p.over5 and p.strange and (abs(p.pid) != 11))
        eff_long_fromb = update_efficiencies(eff_long_fromb, event, tracks, weights, 'long_fromb'
                    , lambda p: p.islong and p.fromb and (abs(p.pid) != 11))
        eff_long_fromb5 = update_efficiencies(eff_long_fromb5, event, tracks, weights, 'long_fromb>5GeV'
                    , lambda p: p.islong and p.over5 and p.fromb and (abs(p.pid) != 11))

    nevents = len(tracking_data)

    #print("Average reconstruction efficiency: %6.2f%% (%d #tracks of %d reconstructible particles)"%(100*avg_recoeff/nevents, n_allreco, n_allparticles))
    print("%d tracks including %8d ghosts (%5.1f%%). Event average %5.1f%%"
        %(n_tracks, n_allghsots, 100.*n_allghsots/n_tracks, 100.*avg_ghost_rate/nevents))
    #print("Number of clones: %d"%n_clones)
    #print("Average hit purity: %6.2f%%"%(100*avg_purity/nevents))
    #print("Average hit efficiency: %6.2f%%"%(100*avg_hiteff/nevents))
    if eff_velo: print(eff_velo)
    if eff_long: print(eff_long)
    if eff_long5: print(eff_long5)
    if eff_long_strange: print(eff_long_strange)
    if eff_long_strange5: print(eff_long_strange5)
    if eff_long_fromb: print(eff_long_fromb)
    if eff_long_fromb5: print(eff_long_fromb5)

def validate(events_json_data, tracks_list, particle_type="long>5GeV"):
    '''Returns just the Efficiency object of the particle_type requested.

    particle_type can be one of {'velo', 'long', 'long>5GeV', 'long_strange',
    'long_strange>5GeV', 'long_fromb', 'long_fromb>5GeV'}.
    '''
    tracking_data = []
    for event, tracks in zip(events_json_data, tracks_list):
        tracking_data.append((parse_json_data(event), tracks))

    particle_lambda = {
        'velo': lambda p: p.isvelo and (abs(p.pid) != 11),
        'long': lambda p: p.islong and (abs(p.pid) != 11),
        'long>5GeV': lambda p: p.islong and p.over5 and (abs(p.pid) != 11),
        'long_strange': lambda p: p.islong and p.strange and (abs(p.pid) != 11),
        'long_strange>5GeV': lambda p: p.islong and p.over5 and p.strange and (abs(p.pid) != 11),
        'long_fromb': lambda p: p.islong and p.fromb and (abs(p.pid) != 11),
        'long_fromb>5GeV': lambda p: p.islong and p.over5 and p.fromb and (abs(p.pid) != 11)
    }

    eff = None
    for event, tracks in tracking_data:
        weights = comp_weights(tracks, event)
        eff = update_efficiencies(eff, event, tracks, weights, particle_type,
            particle_lambda[particle_type])

    return eff

def validate_efficiency(events_json_data, tracks_list, particle_type="long>5GeV"):
    '''Returns just the Reconstruction Efficiency of the particle_type requested,
    as a value in [0,1].
    '''
    return validate(events_json_data, tracks_list, particle_type).recoeffT / 100.0

def validate_clone_fraction(events_json_data, tracks_list, particle_type="long>5GeV"):
    '''Returns just the Clone Fraction of the particle_type requested,
    as a value in [0,1].
    '''
    eff = validate(events_json_data, tracks_list, particle_type)
    return eff.n_clones / eff.n_reco

def validate_ghost_fraction(events_json_data, tracks_list):
    '''Returns just the Clone Fraction of the particle_type requested,
    as a value in [0, 1].
    '''
    tracking_data = []
    for event, tracks in zip(events_json_data, tracks_list):
        tracking_data.append((parse_json_data(event), tracks))

    n_tracks = 0
    avg_ghost_rate = 0.0
    n_allghsots = 0
    for event, tracks in tracking_data:
        n_tracks += len(tracks)
        weights = comp_weights(tracks, event)
        t2p, _ = hit_purity(tracks, event.particles, weights)
        grate, nghosts = ghost_rate(t2p)
        n_allghsots += nghosts
        avg_ghost_rate += grate

    return n_allghsots / n_tracks
