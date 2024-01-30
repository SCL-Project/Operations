// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VotingSystem {
    mapping(uint => uint) public votes; // Maps participant ID to their vote count
    mapping(address => bool) public hasVoted; // Tracks whether an address has voted or not

    uint public votingEnd; // Timestamp of the blockchain when voting ends
    uint public winner; // ID of the winning participant
    bool public votingFinished; // Boolndicate if voting has ended

    event Voted(address voter, uint participant);
    event VotingEnded(uint winningParticipant);

    constructor(uint _votingPeriodInSeconds) {
        votingEnd = block.timestamp + _votingPeriodInSeconds;
    }

    function vote(uint participantId) external {
        require(block.timestamp <= votingEnd, "Voting has ended");
        require(!hasVoted[msg.sender], "You have already voted");
        require(participantId < 20, "Invalid participant ID");

        votes[participantId]++;
        hasVoted[msg.sender] = true;

        emit Voted(msg.sender, participantId);
    }

    function computeWinner() external {
        require(block.timestamp > votingEnd, "Voting is still ongoing");
        require(!votingFinished, "Winner has already been computed");

        uint winningVoteCount = 0;
        for (uint i = 0; i < 20; i++) {
            if (votes[i] > winningVoteCount) {
                winningVoteCount = votes[i];
                winner = i;
            }
        }

        votingFinished = true;
        emit VotingEnded(winner);
    }
}