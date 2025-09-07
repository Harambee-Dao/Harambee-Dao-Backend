from typing import Dict
from collections import defaultdict
from app.models.schemas import VoteIn, VoteOut

# naive in-memory store for demo/tests
_VOTES: Dict[str, Dict[str, bool]] = defaultdict(dict)


def record_vote(v: VoteIn) -> VoteOut:
    # Check if member already voted on this proposal
    if v.memberId in _VOTES[v.proposalId]:
        raise ValueError(f"Member {v.memberId} already voted on proposal {v.proposalId}")

    _VOTES[v.proposalId][v.memberId] = v.vote
    tally = get_vote_tally(v.proposalId)
    return VoteOut(**{"memberId": v.memberId, "proposalId": v.proposalId, "vote": v.vote, "tally": tally})


def get_vote_tally(proposal_id: str):
    votes = _VOTES.get(proposal_id, {})
    yes = sum(1 for _, val in votes.items() if val)
    no = sum(1 for _, val in votes.items() if not val)
    total = len(votes)
    return {"yes": yes, "no": no, "total": total}
