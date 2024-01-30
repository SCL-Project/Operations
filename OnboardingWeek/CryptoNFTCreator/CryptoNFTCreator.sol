// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract CryptoCollectibleCreator is ERC721URIStorage {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;

    // Event declaration
    event CollectibleMinted(address indexed owner, uint256 indexed tokenId);

    constructor() ERC721("CryptoCollectibleCreator", "CCC") {}

    function createCollectible(string memory tokenURI) public returns (uint256) {
        _tokenIds.increment();

        uint256 newItemId = _tokenIds.current();
        _mint(msg.sender, newItemId);
        _setTokenURI(newItemId, tokenURI);

        // Emit the event after minting the NFT
        emit CollectibleMinted(msg.sender, newItemId);

        return newItemId;
    }
}
