// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract EVoting {
    address public owner;

    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized");
        _;
    }

    struct Voter {
        bool isRegistered;
        bool hasVoted;
    }

    struct Candidate {
        uint256 id;
        string name;
        uint256 voteCount;
    }

    struct Election {
        uint256 id;
        string name;
        bool isActive;
        uint256 startTime;
        uint256 endTime;
        uint256 candidateCount;
        mapping(uint256 => Candidate) candidates;
        mapping(bytes32 => Voter) voters; // voterIdHash → Voter
    }

    uint256 public electionCount;
    mapping(uint256 => Election) private elections;

    // EVENTS (These give you auditability on-chain)
    event ElectionCreated(uint256 indexed electionId, string name);
    event CandidateAdded(uint256 indexed electionId, uint256 candidateId, string name);
    event VoterRegistered(uint256 indexed electionId, bytes32 indexed voterIdHash);
    event VoteCast(
        uint256 indexed electionId,
        bytes32 indexed voterIdHash,
        uint256 indexed candidateId
    );

    constructor() {
        owner = msg.sender;
    }

    // ---------------------------------------------------
    // ADMIN FUNCTIONS
    // ---------------------------------------------------

    function createElection(
        string memory _name,
        uint256 _startTime,
        uint256 _endTime
    ) external onlyOwner {
        require(_endTime > _startTime, "Invalid time range");

        electionCount++;
        Election storage e = elections[electionCount];
        e.id = electionCount;
        e.name = _name;
        e.startTime = _startTime;
        e.endTime = _endTime;
        e.isActive = true;

        emit ElectionCreated(electionCount, _name);
    }

    function addCandidate(
        uint256 _electionId,
        string memory _name
    ) external onlyOwner {
        Election storage e = elections[_electionId];
        require(e.id != 0, "Election not found");

        e.candidateCount++;
        uint256 candidateId = e.candidateCount;

        e.candidates[candidateId] = Candidate({
            id: candidateId,
            name: _name,
            voteCount: 0
        });

        emit CandidateAdded(_electionId, candidateId, _name);
    }

    function registerVoter(
        uint256 _electionId,
        bytes32 voterIdHash
    ) external onlyOwner {
        Election storage e = elections[_electionId];
        require(e.id != 0, "Election not found");

        Voter storage v = e.voters[voterIdHash];
        require(!v.isRegistered, "Voter already registered");

        v.isRegistered = true;
        v.hasVoted = false;

        emit VoterRegistered(_electionId, voterIdHash);
    }

    // Backend calls this on behalf of users
    function voteOnBehalf(
        uint256 _electionId,
        bytes32 voterIdHash,
        uint256 candidateId
    ) external onlyOwner {

        Election storage e = elections[_electionId];
        require(e.isActive, "Election inactive");

        require(block.timestamp >= e.startTime, "Voting not started");
        require(block.timestamp <= e.endTime, "Voting ended");

        Voter storage v = e.voters[voterIdHash];
        require(v.isRegistered, "Not registered");
        require(!v.hasVoted, "Already voted");

        Candidate storage c = e.candidates[candidateId];
        require(c.id != 0, "Candidate not found");

        v.hasVoted = true;
        c.voteCount++;

        emit VoteCast(_electionId, voterIdHash, candidateId);
    }

    // ---------------------------------------------------
    // READ-ONLY FUNCTIONS (Frontend/backend use these)
    // ---------------------------------------------------

    function getCandidate(
        uint256 electionId,
        uint256 candidateId
    ) external view returns (string memory name, uint256 votes) {
        Election storage e = elections[electionId];
        Candidate storage c = e.candidates[candidateId];
        return (c.name, c.voteCount);
    }

    function getElectionMeta(
        uint256 electionId
    ) external view returns (
        string memory name,
        bool active,
        uint256 start,
        uint256 end,
        uint256 candidateCount
    ) {
        Election storage e = elections[electionId];
        return (e.name, e.isActive, e.startTime, e.endTime, e.candidateCount);
    }
}
